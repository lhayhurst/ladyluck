from collections import OrderedDict
import os
from flask import url_for
from parser import LogFileParser
from persistence import Game, DiceThrowResult, DiceThrow, DiceThrowType, DiceThrowAdjustmentType, DiceFace, DiceType
from tests.persistence_tests import DatabaseTestCase

__author__ = 'lhayhurst'
import unittest


class DiceStats:
    def __init__(self, player):

        self.player       = player
        self.total_reds   = 0
        self.total_greens = 0

        self.red_hits     = 0
        self.red_blanks   = 0
        self.red_eyes     = 0
        self.red_crits    = 0

        self.green_evades = 0
        self.green_blanks = 0
        self.green_eyes   = 0

        self.num_red_focuses_converted = 0
        self.num_green_focuses_converted = 0


    def set_num_red_focuses_converted(self, count):
        self.num_red_focuses_converted = count

    def red_focuses_converted(self):
        return self.num_red_focuses_converted

    def set_num_green_focuses_converted(self, count):
        self.num_green_focuses_converted = count

    def green_focuses_converted(self):
        return self.num_green_focuses_converted

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

    def add_roll(self, roll, type):
        if type == 'Attack':
            self.total_reds += 1
            if roll.get_result() == 'Hit':
                self.red_hits += 1
            elif roll.get_result() == 'Crit':
                self.red_crits += 1
            elif roll.get_result() == 'Focus':
                self.red_eyes += 1
            elif roll.get_result() == 'Blank':
                self.red_blanks += 1
            else:
                RuntimeError ("unknown dice type, wtf?!")
        elif type == 'Defend':
            self.total_greens += 1
            if roll.get_result() == 'Evade':
                self.green_evades += 1
            elif roll.get_result() == 'Focus':
                self.green_eyes += 1
            elif roll.get_result() == 'Blank':
                self.green_blanks += 1
            else:
                RuntimeError ("unknown dice type, wtf?!")

    def expected_red_hits(self):
        t = self.total_reds
        return t * (3.0 / 8.0)

    def expected_red_misses(self):
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



class GameTapeRecord:


    def __init__(self):
        self.dice_num   = None
        self.throw_num  = None
        self.attack_roll = None
        self.attack_reroll = None
        self.attack_convert = None
        self.attack_end = None
        self.defense_roll = None
        self.defense_reroll = None
        self.defense_convert = None
        self.defense_end = None
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

    def was_not_a_hit_or_crit(self):
        if self.was_hit() == True or self.was_crit() == True:
            return False
        return True

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

    def was_hit(self):
        if self.attack_end == None:
            return False
        return self.attack_end.dice_face == DiceFace.HIT

    def was_crit(self):
        if self.attack_end == None:
            return False

        return self.attack_end.dice_face == DiceFace.CRIT

    def was_evade(self):
        if self.defense_end == None:
            return False
        return self.defense_end.dice_face == DiceFace.EVADE


class AttackSet:
    def __init__(self, attack_set):
        self.number = attack_set
        self.records = []
        self.attacking_player = None
        self.defending_player = None

    def get_record_for_dice_num(self, dice_num):
        for rec in self.records:
            if rec.dice_num == dice_num:
                return rec
        return None

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


class GameTape(object):

    def get_attack_set(self, attack_set_num):
        for aset in self.attack_sets:
            if aset.number == attack_set_num:
                return aset
        return None

    def __init__(self, game):

        self.game = game
        throws = self.game.game_throws

        attack_sets = []
        self.attack_sets = attack_sets

        #do the attack sets first
        for throw in throws:
            if throw.throw_type == DiceThrowType.ATTACK:
                attack_set = AttackSet( throw.attack_set_num )
                attack_sets.append( attack_set )
                attack_set.attacking_player = throw.player.name

                for result in throw.results:
                    record = GameTapeRecord()
                    attack_set.records.append(record)
                    record.dice_num = result.dice_num
                    record.attack_roll = result.dice
                    record.attack_end = result.final_dice
                    for adjustment in result.adjustments:
                        record.visit(adjustment, "attack")

            elif throw.throw_type == DiceThrowType.DEFEND:
                attack_set = self.get_attack_set(throw.attack_set_num)
                for result in throw.results:
                    attack_set.defending_player = throw.player.name
                    record = attack_set.get_record_for_dice_num( result.dice_num )
                    if record is not None:
                        record = attack_set.get_record_for_dice_num( result.dice_num )
                        record.defense_roll = result.dice
                        record.defense_end = result.final_dice
                        for adjustment in result.adjustments:
                            record.visit(adjustment, "defense")
                    else:
                        record = GameTapeRecord()
                        attack_set.records.append(record)
                        record.dice_num = result.dice_num
                        record.defense_roll = result.dice
                        record.defense_end = result.final_dice
                        for adjustment in result.adjustments:
                            record.visit(adjustment, "defense")

        #now circle through all the records and net out the records
        for ats in self.attack_sets:
            ats.net_results()

class GameTapeTester(unittest.TestCase):

    def testSummaryStats(self):
        parser = LogFileParser()
        parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()
        game_tape = parser.game_tape

        g = Game(parser.get_players())


        for throw_result in game_tape:
            g.game_throws.append(throw_result)

        tape = GameTape( g )
        self.assertEqual( 4, len(tape.attack_sets) )

        aset = tape.attack_sets[0]
        records = aset.records
        self.assertEqual( 3, len(records ))
        self.assertEqual( "Ryan Krippendorf", aset.attacking_player)
        self.assertEqual( "sozin", aset.defending_player)

        rec = records[0]
        self.assertEqual( aset.number, 1 )
        self.assertEqual( 1, rec.dice_num )
        self.assertEqual( rec.attack_roll.dice_face, DiceFace.FOCUS )
        self.assertEqual( rec.attack_roll.dice_type, DiceType.RED )
        self.assertEqual( rec.attack_roll.dice_face, DiceFace.FOCUS )
        self.assertEqual( rec.attack_roll.dice_type, DiceType.RED )


if __name__ == "__main__":
    unittest.main()


