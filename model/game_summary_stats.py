from collections import OrderedDict
import os
from flask import url_for
from parser import LogFileParser
from persistence import Game, DiceThrowResult, DiceThrow, DiceThrowType, DiceThrowAdjustmentType, DiceFace, DiceType
from tape_graph import TapeGraph
from tests.persistence_tests import DatabaseTestCase

__author__ = 'lhayhurst'
import unittest

class Counter:
    def __init__(self):

        self.total_reds   = 0
        self.total_greens = 0

        self.red_hits     = 0
        self.red_blanks   = 0
        self.red_eyes     = 0
        self.red_crits    = 0

        self.green_evades = 0
        self.green_blanks = 0
        self.green_eyes   = 0


    def red_hit_differential(self):
        return self.red_hits - self.expected_red_hits()

    def red_crit_differential(self):
        return self.red_crits - self.expected_red_crits()

    def red_focus_differential(self):
        return self.red_eyes - self.expected_red_eyes()

    def red_blank_differential(self):
        return self.expected_red_misses() - self.red_blanks

    def green_evade_differential(self):
        return self.green_evades - self.expected_green_evades()

    def green_eyes_differential(self):
        return self.green_eyes - self.expected_green_eyes()

    def green_blank_differential(self):
        return self.expected_green_blanks() - self.green_blanks

    def count(self, roll ):
        if roll.is_attack():
            self.total_reds += 1
            if roll.is_hit():
                self.red_hits += 1
            elif roll.is_crit():
                self.red_crits += 1
            elif roll.is_focus():
                self.red_eyes += 1
            elif roll.is_blank():
                self.red_blanks += 1
        elif roll.is_defense():
            self.total_greens += 1
            if roll.is_evade():
                self.green_evades += 1
            elif roll.is_focus():
                self.green_eyes += 1
            elif roll.is_blank():
                self.green_blanks += 1
        return self

    def expected_red_hits(self):
        t = self.total_reds
        return t * (3.0 / 8.0)

    def expected_red_blanks(self):
        t = self.total_reds
        return t * (2.0 / 8.0)

    def expected_red_crits(self ):
        t = self.total_reds
        return t * (1.0 / 8.0)

    def expected_red_eyes(self):
        t = self.total_reds
        return t * (2.0 / 8.0)

    def expected_green_evades(self):
        t = self.total_greens
        return t * (3.0 / 8.0)

    def expected_green_blanks(self):
        t = self.total_greens
        return t * (3.0 / 8.0)

    def expected_green_eyes(self ):
        t = self.total_greens
        return t * (2.0 / 8.0)

class Score:

    HIT_WEIGHT         = 1
    CRIT_WEIGHT        = 1.25
    RED_FOCUS_WEIGHT   = 0.5
    RED_BLANK_WEIGHT   = 0
    EVADE_WEIGHT       = 1
    GREEN_FOCUS_WEIGHT = 0.75
    GREEN_BLANK_WEIGHT = 0

    def __init__(self):
        self.red_luck   = []
        self.green_luck = []

    def get_last_red_luck(self):
        if len(self.red_luck) > 0:
            return self.red_luck[-1]
        else:
            return None

    def get_last_green_luck(self):
        if len(self.green_luck) > 0:
            return self.green_luck[-1]
        else:
            return None


    def eval(self, dice_type, counter):
        if dice_type == DiceType.RED:
            return self.eval_red(counter)
        elif dice_type == DiceType.GREEN:
            return self.eval_green(counter)

    def eval_red(self, counter):

        exp_hits         = counter.expected_red_hits()
        hit_dev          = counter.red_hits - exp_hits
        weighted_hit_dev = hit_dev * Score.HIT_WEIGHT

        exp_crits         = counter.expected_red_crits()
        crit_dev          = counter.red_crits - exp_crits
        weighted_crit_dev = crit_dev * Score.CRIT_WEIGHT

        exp_focus          = counter.expected_red_eyes()
        focus_dev          = counter.red_eyes - exp_focus
        weighted_focus_dev = focus_dev * Score.RED_FOCUS_WEIGHT

        exp_blank          = counter.expected_red_blanks()
        blank_dev          = counter.red_blanks - exp_blank
        weighted_blank_dev = blank_dev * Score.RED_BLANK_WEIGHT

        luck = weighted_hit_dev + weighted_crit_dev + weighted_focus_dev + weighted_blank_dev

        self.red_luck.append(luck)

        return luck

    def eval_green(self, counter):
        exp_evades         = counter.expected_green_evades()
        evade_dev          = counter.green_evades - exp_evades
        weighted_evade_dev = evade_dev * Score.EVADE_WEIGHT

        exp_focus          = counter.expected_green_eyes()
        focus_dev          = counter.green_eyes - exp_focus
        weighted_focus_dev = focus_dev * Score.GREEN_FOCUS_WEIGHT

        exp_blank          = counter.expected_green_blanks()
        blank_dev          = counter.green_blanks - exp_blank
        weighted_blank_dev = blank_dev * Score.GREEN_BLANK_WEIGHT

        luck = weighted_evade_dev + weighted_focus_dev + weighted_blank_dev

        self.green_luck.append(luck)

        return luck

class GameTapeRecord:


    def __init__(self, attacking_player, defending_player):
        self.attacking_player = attacking_player
        self.defending_player = defending_player
        self.dice_num   = None
        self.throw_num  = None
        self.attack_roll = None
        self.attack_roll_luck = None
        self.attack_reroll = None
        self.attack_reroll_luck = None
        self.attack_convert = None
        self.attack_convert_luck = None
        self.attack_end = None
        self.attack_end_luck = None
        self.defense_roll = None
        self.defense_luck = None
        self.defense_reroll = None
        self.defense_reroll_luck = None
        self.defense_convert = None
        self.defense_convert_luck = None
        self.defense_end = None
        self.defense_end_luck = None
        self.was_cancelled = False

    def cancel(self):
        self.was_cancelled = True

    def get_image(self, dice):
        if dice == None:
            return url_for( 'static', filename='blank.png')
        if dice.dice_type == DiceType.RED:
            if dice.dice_face == DiceFace.HIT:
                return url_for( 'static', filename="red_hit.png")
            elif dice.dice_face == DiceFace.CRIT:
                return url_for( 'static',filename="red_crit.png")
            elif dice.dice_face == DiceFace.FOCUS:
                return url_for( 'static',filename="red_focus.png")
            elif dice.dice_face == DiceFace.BLANK:
                return url_for( 'static',filename="red_blank.png")
        else:
            if dice.dice_face == DiceFace.EVADE:
                return url_for( 'static',filename="green_evade.png")
            elif dice.dice_face == DiceFace.FOCUS:
                return url_for( 'static',filename="green_focus.png")
            elif dice.dice_face == DiceFace.BLANK:
                return url_for( 'static',filename="green_blank.png")

    def final_as_image(self):
        if self.was_cancelled == True:
           return self.get_image(None)
        elif self.was_not_a_hit_or_crit() == True:
            return self.get_image(None)
        else:
            return self.attack_end_as_img()

    def attack_roll_as_img(self):
        return self.get_image(self.attack_roll)

    def attack_reroll_as_img(self):
        return self.get_image(self.attack_reroll)

    def attack_convert_as_img(self):
        return self.get_image(self.attack_convert)

    def attack_end_as_img(self):
        return self.get_image(self.attack_end)

    def defense_roll_as_img(self):
        return self.get_image(self.defense_roll)

    def defense_reroll_as_img(self):
        return self.get_image(self.defense_reroll)

    def defense_convert_as_img(self):
        return self.get_image(self.defense_convert)

    def defense_end_as_img(self):
        return self.get_image(self.defense_end)

    def visit(self, adjustment, atype):
        if adjustment.adjustment_type == DiceThrowAdjustmentType.REROLL:
            if atype == "attack":
                self.attack_reroll = adjustment.to_dice
            elif atype == "defense":
                self.defense_reroll = adjustment.to_dice
        elif adjustment.adjustment_type == DiceThrowAdjustmentType.CONVERT:
            if atype == "attack":
                self.attack_convert = adjustment.to_dice
            elif atype == "defense":
                self.defense_convert = adjustment.to_dice

    def was_not_a_hit_or_crit(self):
        if self.was_hit() == True or self.was_crit() == True:
            return False
        return True

    def was_hit(self):
        if self.attack_end == None:
            return False
        return self.attack_end.is_hit()

    def was_crit(self):
        if self.attack_end == None:
            return False

        return self.attack_end.is_crit()

    def was_evade(self):
        if self.defense_end == None:
            return False
        return self.defense_end.is_evade()

class AttackSet:
    def __init__(self, attack_set, throw):
        self.attacking_throw = throw
        self.number = attack_set
        self.records = []
        self.attacking_player = None
        self.defending_player = None
        self.cumulative_score = None

    def add_defending_throw(self, throw):
        self.defending_throw = throw
        self.defending_player = throw.player

    def get_record_for_dice_num(self, dice_num):
        for rec in self.records:
            if rec.dice_num == dice_num:
                return rec
        return None


    def cumulative_attack_luck(self):
        return self.cumulative_attack_score

    def cumulative_defense_luck(self):
        return self.cumulative_defense_score

    def total_attack_roll_luck(self):
        return self.total_by_luck_attr("attack_roll_luck")

    def total_attack_reroll_luck(self):
        return self.total_by_luck_attr("attack_reroll_luck")

    def total_attack_convert_luck(self):
        return self.total_by_luck_attr("attack_convert_luck")

    def total_attack_end_luck(self):
        return self.total_by_luck_attr("attack_end_luck")

    def total_defense_roll_luck(self):
        return self.total_by_luck_attr("defense_roll_luck")

    def total_defense_reroll_luck(self):
        return self.total_by_luck_attr("defense_reroll_luck")

    def total_defense_convert_luck(self):
        return self.total_by_luck_attr("defense_convert_luck")

    def total_defense_end_luck(self):
        return self.total_by_luck_attr("defense_end_luck")



    def total_by_luck_attr(self, attr):
        score = None
        for rec in self.records:
            if hasattr( rec, attr) and getattr(rec, attr) is not None:
                if score is None:
                    score = getattr(rec, attr)
                else:
                    score = getattr(rec, attr)
        return score

    def get_hits(self):
        ret = []
        for rec in self.records:
            if rec.was_hit():
                ret.append(rec)
        return ret

    def get_crits(self):
        ret = []
        for rec in self.records:
            if rec.was_crit():
                ret.append(rec)
        return ret

    def get_evades(self):
        ret = []
        for rec in self.records:
            if rec.was_evade():
                ret.append(rec)
        return ret


    def net_results(self):
        #first extract all the hits
        hits = self.get_hits()
        #then crits
        crits = self.get_crits()

        if len(hits) == 0 and len(crits) == 0:
            return

        evades = self.get_evades()
        num_evades = len(evades)

        #first cancel the hits
        for hit in hits:
            if num_evades > 0:
                num_evades = num_evades - 1
                hit.cancel()
            elif num_evades == 0:
                break

        #now try to cancel the crits
        for crit in crits:
            if num_evades > 0:
                num_evades = num_evades - 1
                crit.cancel()
            elif num_evades == 0:
                break


    def score(self, cumulative_counter, cumulative_score, tape_stats):

        self.roll_counter              = Counter()
        self.reroll_counter            = Counter()
        self.convert_counter           = Counter()
        self.end_counter               = Counter()
        self.roll_score                = Score()
        self.reroll_score              = Score()
        self.convert_score             = Score()
        self.end_score                 = Score()

        for rec in self.records:
            if rec.attack_roll is not None:
                luck = self.roll_score.eval( rec.attack_roll.dice_type, self.roll_counter.count(rec.attack_roll))
                rec.attack_roll_luck = luck
                tape_stats[rec.attacking_player.name]["score"].eval(
                    rec.attack_roll.dice_type,
                    tape_stats[rec.attacking_player.name]["counter"].count( rec.attack_roll )
                )
            if rec.defense_roll is not None:
                luck = self.roll_score.eval( rec.defense_roll.dice_type, self.roll_counter.count( rec.defense_roll))
                rec.defense_roll_luck = luck
                if rec.defending_player is not None:
                    tape_stats[rec.defending_player.name]["score"].eval(
                        rec.defense_roll.dice_type,
                        tape_stats[rec.defending_player.name]["counter"].count( rec.defense_roll )
                    )
            if rec.attack_reroll is not None:
                luck = self.reroll_score.eval( rec.attack_reroll.dice_type, self.reroll_counter.count(rec.attack_reroll))
                rec.attack_reroll_luck = luck
            if rec.defense_reroll is not None:
                luck = self.reroll_score.eval( rec.defense_reroll.dice_type, self.reroll_counter.count(rec.defense_reroll))
                rec.defense_reroll_luck = luck
            if rec.attack_convert is not None:
                luck = self.convert_score.eval( rec.attack_convert.dice_type, self.convert_counter.count(rec.attack_convert))
                rec.attack_convert_luck = luck
            if rec.defense_convert is not None:
                luck = self.convert_score.eval( rec.defense_convert.dice_type, self.convert_counter.count(rec.defense_convert))
                rec.defense_convert_luck = luck
            if rec.attack_end is not None:
                luck = self.end_score.eval( rec.attack_end.dice_type, self.end_counter.count(rec.attack_end))
                rec.attack_end_luck = luck
                cumulative_score.eval( rec.attack_end.dice_type, cumulative_counter.count(rec.attack_end))

            if rec.defense_end is not None:
                luck = self.end_score.eval( rec.defense_end.dice_type, self.end_counter.count(rec.defense_end))
                rec.defense_end_luck = luck
                cumulative_score.eval( rec.defense_end.dice_type, cumulative_counter.count(rec.defense_end))

        self.cumulative_attack_score = cumulative_score.get_last_red_luck()
        self.cumulative_defense_score = cumulative_score.get_last_green_luck()

class GameTape(object):

    def get_attack_set(self, attack_set_num):
        for aset in self.attack_sets:
            if aset.number == attack_set_num:
                return aset
        return None

    def unmodified_attack_data(self, player):
        return self.stats[player]["score"].red_luck

    def total_reds(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].total_reds

    def total_greens(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].total_greens

    def unmodified_hits(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].red_hits


    def expected_unmodified_hits(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].expected_red_hits()

    def unmodified_evades(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].green_evades


    def expected_unmodified_evades(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].expected_green_evades()

    def unmodified_crits(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].red_crits


    def expected_unmodified_focuses(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].expected_red_eyes()

    def unmodified_focuses(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].red_eyes

    def expected_unmodified_green_focuses(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].expected_green_eyes()

    def unmodified_green_focuses(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].green_eyes


    def expected_unmodified_blanks(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].expected_red_blanks()

    def unmodified_blanks(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].red_blanks

    def expected_unmodified_green_blanks(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].expected_green_blanks()

    def unmodified_green_blanks(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].green_blanks

    def expected_unmodified_crits(self, player):
        if self.stats == None:
            return 0
        else:
            return self.stats[player.name]["counter"].expected_red_crits()

    def __init__(self, game):

        self.game = game
        game.game_tape = self
        throws = self.game.game_throws

        attack_sets = []
        self.attack_sets = attack_sets

        #do the attack sets first
        for throw in throws:
            if throw.throw_type == DiceThrowType.ATTACK:
                attack_set = AttackSet( throw.attack_set_num, throw )
                attack_sets.append( attack_set )
                attack_set.attacking_player = throw.player

                for result in throw.results:
                    record = GameTapeRecord( attacking_player=attack_set.attacking_player, defending_player=attack_set.defending_player)
                    attack_set.records.append(record)
                    record.dice_num = result.dice_num
                    record.attack_roll = result.dice
                    record.attack_end = result.final_dice
                    for adjustment in result.adjustments:
                        record.visit(adjustment, "attack")

            elif throw.throw_type == DiceThrowType.DEFEND:
                attack_set = self.get_attack_set(throw.attack_set_num)
                attack_set.add_defending_throw(throw)
                for result in throw.results:
                    record = attack_set.get_record_for_dice_num( result.dice_num )
                    if record is not None:
                        record = attack_set.get_record_for_dice_num( result.dice_num )
                        record.defending_player = throw.player
                        record.defense_roll = result.dice
                        record.defense_end = result.final_dice
                        for adjustment in result.adjustments:
                            record.visit(adjustment, "defense")
                    else:
                        record = GameTapeRecord(attacking_player=attack_set.attacking_player, defending_player=throw.player)
                        attack_set.records.append(record)
                        record.dice_num = result.dice_num
                        record.defense_roll = result.dice
                        record.defense_end = result.final_dice
                        for adjustment in result.adjustments:
                            record.visit(adjustment, "defense")

        #now circle through all the records and net out the records
        for ats in self.attack_sets:
            ats.net_results()

    def score(self):
        raw_luck_p1          = Counter()
        raw_score_p1         = Score()
        raw_luck_p2          = Counter()
        raw_score_p2         = Score()

        self.stats = {}
        self.stats[ self.game.game_players[0].name] = { "counter" : raw_luck_p1, "score" : raw_score_p1 }
        self.stats[ self.game.game_players[1].name] = { "counter" : raw_luck_p2, "score" : raw_score_p2 }


        cumulative_luck      = Counter()
        cumulative_score     = Score()

        for ats in self.attack_sets:
            ats.score(cumulative_luck, cumulative_score, self.stats)

        self.cumulative_luck  = cumulative_luck
        self.cumulative_score = cumulative_score


class GameTapeTester(unittest.TestCase):

    def setUp(self):

        self.parser = LogFileParser()
        self.parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        self.parser.run_finite_state_machine()
        self.game_tape = self.parser.game_tape

        self.g = Game(self.parser.get_players())


        for throw_result in self.game_tape:
            self.g.game_throws.append(throw_result)

        self.tape = GameTape( self.g )
        self.tape.score()


    def testRawSummaryStats(self):

        self.assertEqual( 4, self.g.total_reds( self.g.game_players[0] ) )
        self.assertEqual( 1, self.g.unmodified_hits( self.g.game_players[0] ) )
        self.assertEqual( (3.0/8.0) * 4 , self.g.expected_unmodified_hits( self.g.game_players[0] ) )

        self.assertEqual( 4, self.g.total_greens(self.g.game_players[1]))

    def testAttackSetStats(self):

        self.assertEqual( 4, len(self.tape.attack_sets) )

        aset = self.tape.attack_sets[0]
        self.assertEqual( -.8125, aset.total_attack_roll_luck() )
        self.assertEqual( None, aset.total_attack_reroll_luck())
        self.assertEqual( .34375, aset.total_attack_convert_luck() )
        self.assertEqual( -.3125, aset.total_attack_end_luck() )
        self.assertEqual( -.3125, aset.cumulative_attack_luck() )

        self.assertEqual( .3125, aset.total_defense_roll_luck() )
        self.assertEqual( None, aset.total_defense_reroll_luck())
        self.assertEqual( None, aset.total_defense_convert_luck() )
        self.assertEqual( .3125, aset.total_defense_end_luck() )
        self.assertEqual( 0.3125, aset.cumulative_defense_luck() )


        aset = self.tape.attack_sets[1]
        self.assertEqual( .9375, aset.total_attack_roll_luck() )
        self.assertEqual( None, aset.total_attack_reroll_luck())
        self.assertEqual( None, aset.total_attack_convert_luck() )
        self.assertEqual( .9375, aset.total_attack_end_luck() )
        self.assertEqual( 0.625, aset.cumulative_attack_luck() )


        self.assertEqual( 0.1875, aset.total_defense_roll_luck() )
        self.assertEqual( None, aset.total_defense_reroll_luck())
        self.assertEqual( 0.4375, aset.total_defense_convert_luck() )
        self.assertEqual( 0.4375, aset.total_defense_end_luck() )
        self.assertEqual( 0.75, aset.cumulative_defense_luck() )


        aset = self.tape.attack_sets[2]
        self.assertEqual( -1.3125, aset.total_attack_roll_luck() )
        self.assertEqual( -0.3125, aset.total_attack_reroll_luck())
        self.assertEqual( 0.6875, aset.total_attack_convert_luck() )
        self.assertEqual( 0.6875, aset.total_attack_end_luck() )
        self.assertEqual( 1.3125, aset.cumulative_attack_luck() )


        self.assertEqual( -0.1875, aset.total_defense_roll_luck() )
        self.assertEqual( 0.1875, aset.total_defense_reroll_luck())
        self.assertEqual( 1.3125, aset.total_defense_convert_luck() )
        self.assertEqual( 1.3125, aset.total_defense_end_luck() )
        self.assertEqual( 2.0625, aset.cumulative_defense_luck() )


        aset = self.tape.attack_sets[3]
        self.assertEqual( 0.59375, aset.total_attack_roll_luck() )
        self.assertEqual( None, aset.total_attack_reroll_luck())
        self.assertEqual( None, aset.total_attack_convert_luck() )
        self.assertEqual( 0.59375, aset.total_attack_end_luck() )
        self.assertEqual( 1.90625, aset.cumulative_attack_luck() )


        self.assertEqual( -0.9375, aset.total_defense_roll_luck() )
        self.assertEqual( None, aset.total_defense_reroll_luck())
        self.assertEqual(0.4375, aset.total_defense_convert_luck() )
        self.assertEqual( -0.6875, aset.total_defense_end_luck() )
        self.assertEqual( 1.375, aset.cumulative_defense_luck() )


if __name__ == "__main__":
    unittest.main()


