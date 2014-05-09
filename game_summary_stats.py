import collections
from flask import url_for

from AttackSet import AttackSet, INITIAL, SCORE, END
from counter import Counter, COUNTER
from parser import LogFileParser
from persistence import Game, DiceThrowType, DiceThrowAdjustmentType, DiceFace, DiceType
from score import Score

STATIC = 'static'


__author__ = 'lhayhurst'
import unittest


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
            return url_for(STATIC, filename='blank.png')
        if dice.dice_type == DiceType.RED:
            if dice.dice_face == DiceFace.HIT:
                return url_for(STATIC, filename="red_hit.png")
            elif dice.dice_face == DiceFace.CRIT:
                return url_for(STATIC,filename="red_crit.png")
            elif dice.dice_face == DiceFace.FOCUS:
                return url_for(STATIC,filename="red_focus.png")
            elif dice.dice_face == DiceFace.BLANK:
                return url_for(STATIC,filename="red_blank.png")
        else:
            if dice.dice_face == DiceFace.EVADE:
                return url_for(STATIC,filename="green_evade.png")
            elif dice.dice_face == DiceFace.FOCUS:
                return url_for(STATIC,filename="green_focus.png")
            elif dice.dice_face == DiceFace.BLANK:
                return url_for(STATIC,filename="green_blank.png")

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
            if atype == DiceThrowType.ATTACK:
                self.attack_reroll = adjustment.to_dice
            elif atype == DiceThrowType.DEFEND:
                self.defense_reroll = adjustment.to_dice
        elif adjustment.adjustment_type == DiceThrowAdjustmentType.CONVERT:
            if atype == DiceThrowType.ATTACK:
                self.attack_convert = adjustment.to_dice
            elif atype == DiceThrowType.DEFEND:
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

class GameTape(object):

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
                        record.visit(adjustment, DiceThrowType.ATTACK)

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
                            record.visit(adjustment, DiceThrowType.DEFEND)
                    else:
                        record = GameTapeRecord(attacking_player=attack_set.attacking_player, defending_player=throw.player)
                        attack_set.records.append(record)
                        record.dice_num = result.dice_num
                        record.defense_roll = result.dice
                        record.defense_end = result.final_dice
                        for adjustment in result.adjustments:
                            record.visit(adjustment, DiceThrowType.DEFEND)

        #now circle through all the records and net out the records
        for ats in self.attack_sets:
            ats.net_results()


    def attack_set_subsets(self, modvalue=15):
        ret = []
        i = 0
        subset = []
        for ats in self.attack_sets:
            i = i + 1
            if i % modvalue == 0:
                ret.append(list(subset))
                subset = []
            else:
                subset.append( ats )
        if len(subset) > 0:
            ret.append(subset)
        return ret


    def total_attack_sets(self, player):
        cnt = 0
        for ats in self.attack_sets:
            if ats.attacking_player.name == player.name:
                cnt = cnt + 1
        return cnt

    def score(self):

        self.scores = collections.defaultdict( lambda: collections.defaultdict(list))
        self.stats = collections.defaultdict( lambda: collections.defaultdict(dict))

        p1 = self.game.game_players[0].name
        p2 = self.game.game_players[1].name
        self.scores[ p1][ DiceType.RED ].append( 0 )
        self.scores[ p2 ][ DiceType.RED ].append( 0 )
        self.scores[ p1 ][ DiceType.GREEN ].append( 0 )
        self.scores[ p2 ][ DiceType.GREEN ].append( 0 )

        self.stats[ p1 ][INITIAL] = { COUNTER : Counter(True), SCORE: Score() }
        self.stats[ p2 ][INITIAL] = { COUNTER : Counter(True), SCORE: Score() }
        self.stats[ p1 ][END] = { COUNTER : Counter(True), SCORE: Score() }
        self.stats[ p2 ][END] = { COUNTER : Counter(True), SCORE: Score() }

        p1_red_score   = self.scores[ p1 ][ DiceType.RED ]
        p2_red_score   = self.scores[ p2 ][ DiceType.RED ]
        p1_green_score = self.scores[ p1 ][ DiceType.GREEN ]
        p2_green_score = self.scores[ p2 ][ DiceType.GREEN ]


        for ats in self.attack_sets:
            ats.score(self.stats )
            if ats.attacking_player.name == p1:
                p1_red_score.append( ats.cumulative_attack_end_luck )
                p1_green_score.append( p1_green_score[-1])
                p2_red_score.append( p2_red_score[-1])
                p2_green_score.append( ats.cumulative_defense_end_luck )
            else: #p2 is the attacking player
                p2_red_score.append( ats.cumulative_attack_end_luck )
                p2_green_score.append( p2_green_score[-1])
                p1_red_score.append( p1_red_score[-1])
                p1_green_score.append( ats.cumulative_defense_end_luck )



    def red_scores(self, player):
        return self.scores[ player.name][DiceType.RED]

    def green_scores(self, player):
        return self.scores[ player.name][DiceType.GREEN]

    def get_attack_set(self, attack_set_num):
        for aset in self.attack_sets:
            if aset.number == attack_set_num:
                return aset
        return None


    def initial_player_score(self, player):
        return self.stats[player][INITIAL][SCORE]

    def initial_player_counter(self, player):
        return self.stats[player.name][INITIAL][COUNTER]

    def unmodified_attack_data(self, player):
        return self.initial_player_score(player).red_luck


    def total_reds(self, player):
        return self.initial_player_counter(player).total_reds


    #total helper methods methods

    def unmodified_hits(self, player):
        return self.initial_player_counter(player).red_hits

    def total_reds_after_rerolls(self, player):
        return self.initial_player_counter(player).total_reds_after_rerolls()

    def total_greens_after_rerolls(self, player):
        return self.initial_player_counter(player).total_greens_after_rerolls()

    def total_red_hits_after_rerolls(self, player):
        return self.initial_player_counter(player).total_red_hits_after_rerolls()

    def total_red_hits_after_converts(self, player):
        return self.initial_player_counter(player).total_red_hits_after_converts()

    def total_green_evades_after_converts(self, player):
        return self.initial_player_counter(player).total_green_evades_after_converts()

    def total_red_crits_after_rerolls(self, player):
        return self.initial_player_counter(player).total_red_crits_after_rerolls()

    def total_red_crits_after_converts(self, player):
        return self.initial_player_counter(player).total_red_crits_after_converts()

    def total_red_focuses_after_rerolls(self, player):
        return self.initial_player_counter(player).total_red_focuses_after_rerolls()

    def expected_green_focuses_after_rerolls(self, player):
        return self.initial_player_counter(player).expected_green_focuses_after_rerolls()

    def total_red_blanks_after_rerolls(self, player):
        return self.initial_player_counter(player).total_red_blanks_after_rerolls()

    def total_green_evades_after_rerolls(self, player):
        return self.initial_player_counter(player).total_green_evades_after_rerolls()


    def total_red_focuses_after_converts(self, player):
        return self.initial_player_counter(player).total_red_focuses_after_converts()

    def total_red_blanks_after_converts(self, player):
        return self.initial_player_counter(player).total_red_blanks_after_converts()

    def expected_hits_after_rerolls(self, player):
        return self.initial_player_counter(player).expected_hits_after_rerolls()

    def expected_crits_after_rerolls(self, player):
        return self.initial_player_counter(player).expected_crits_after_rerolls()

    def expected_crits_after_converts(self, player):
        return self.initial_player_counter(player).expected_crits_after_rerolls() #converts implies no rerolls


    def expected_hits_after_converts(self, player):
        #its the same name as the re-rolls, since no new dice have been thrown
        return self.expected_hits_after_rerolls(player)

    def expected_focuses_after_rerolls(self, player):
        return self.initial_player_counter(player).expected_focuses_after_rerolls()

    def expected_blanks_after_rerolls(self, player):
        return self.initial_player_counter(player).expected_blanks_after_rerolls()

    def expected_blanks_after_converts(self, player):
        return self.expected_blanks_after_rerolls(player) #count doesn't change


    def expected_focuses_after_converts(self, player):
        return self.expected_focuses_after_rerolls(player) #thecount doesn't go up, so can piggy back

    def expected_green_focuses_after_converts(self, player):
        return self.expected_green_focuses_after_rerolls(player) #thecount doesn't go up, so can piggy back

    def expected_green_blanks_after_converts(self, player):
        return self.expected_green_blanks_after_rerolls(player)

    def expected_green_evades_after_converts(self, player):
        return self.expected_green_evades_after_rerolls(player)

    def total_greens(self, player):
        return self.initial_player_counter(player).total_greens

    def total_green_focuses_after_rerolls(self, player):
        return self.initial_player_counter(player).total_green_focuses_after_rerolls()

    def total_green_focuses_after_converts(self, player):
        return self.initial_player_counter(player).total_green_focuses_after_converts()


    def total_green_blanks_after_rerolls(self, player):
        return self.initial_player_counter(player).total_green_blanks_after_rerolls()

    def total_green_blanks_after_converts(self, player):
        return self.initial_player_counter(player).total_green_blanks_after_converts()


    def expected_unmodified_hits(self, player):
        return self.initial_player_counter(player).expected_red_hits()

    def unmodified_evades(self, player):
        return self.initial_player_counter(player).green_evades


    def expected_unmodified_evades(self, player):
        return self.initial_player_counter(player).expected_green_evades()

    def expected_green_evades_after_rerolls(self, player):
        return self.initial_player_counter(player).expected_green_evades_after_rerolls()

    def unmodified_crits(self, player):
        return self.initial_player_counter(player).red_crits

    def expected_unmodified_focuses(self, player):
        return self.initial_player_counter(player).expected_red_eyes()

    def unmodified_focuses(self, player):
        return self.initial_player_counter(player).red_eyes

    def expected_unmodified_green_focuses(self, player):
        return self.initial_player_counter(player).expected_green_eyes()

    def unmodified_green_focuses(self, player):
        return self.initial_player_counter(player).green_eyes


    def expected_unmodified_blanks(self, player):
        return self.initial_player_counter(player).expected_red_blanks()

    def unmodified_blanks(self, player):
        return self.initial_player_counter(player).red_blanks

    def expected_unmodified_green_blanks(self, player):
        return self.initial_player_counter(player).expected_green_blanks()

    def expected_green_blanks_after_rerolls(self, player):
        return self.initial_player_counter(player).expected_green_blanks_after_rerolls()

    def unmodified_green_blanks(self, player):
        return self.initial_player_counter(player).green_blanks

    def expected_unmodified_crits(self, player):
        return self.initial_player_counter(player).expected_red_crits()



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

    def testCumulativeStats(self):

        p1 = self.g.game_players[0]
        p2 = self.g.game_players[1]

        self.assertEqual( 4, self.g.total_reds( p1) )
        self.assertEqual( 3, self.g.total_reds( p2) )

        p1_reds = self.g.game_tape.red_scores( p1 )

        self.assertEqual( 5, len(p1_reds))
        self.assertEqual( 0, p1_reds[0])
        self.assertEqual( -0.3125, p1_reds[1])
        self.assertEqual(  0.625, p1_reds[2])
        self.assertEqual(  0.625, p1_reds[3])
        self.assertEqual(  0.625, p1_reds[4])


        p2_reds = self.g.game_tape.red_scores( p2 )

        self.assertEqual( 5, len(p2_reds))
        self.assertEqual( 0, p2_reds[0])
        self.assertEqual( 0, p2_reds[1])
        self.assertEqual( 0, p2_reds[2])
        self.assertEqual( 0.9375, p2_reds[3])
        self.assertEqual( 1.53125, p2_reds[4])


        p1_greens = self.g.game_tape.green_scores( p1 )

        self.assertEqual( 5, len(p1_greens))

        self.assertEqual(0, p1_greens[0])
        self.assertEqual(0, p1_greens[1])
        self.assertEqual(0, p1_greens[2])
        self.assertEqual(1.3125, p1_greens[3])
        self.assertEqual(0.625, p1_greens[4])

        p2_greens = self.g.game_tape.green_scores( p2 )

        print p2_greens
        self.assertEqual( 5, len(p2_greens))
        self.assertEqual( 0, p2_greens[0])
        self.assertEqual( 0.3125, p2_greens[1])
        self.assertEqual( 0.75, p2_greens[2])
        self.assertEqual( 0.75, p2_greens[3])
        self.assertEqual( 0.75, p2_greens[4])





    def testRawSummaryStats(self):

        p1 = self.g.game_players[0]
        p2 = self.g.game_players[1]

        #HITS

        #totals first
        self.assertEqual( 4, self.g.total_reds( p1) )
        self.assertEqual( 3, self.g.total_reds( p2) )


        #p1, initial rolls
        self.assertEqual( 1, self.g.unmodified_hits( p1 ) )
        self.assertEqual( (3.0/8.0) * 4 , self.g.expected_unmodified_hits( p1 ) )

        #p2, initial roles
        self.assertEqual( 0, self.g.unmodified_hits( p2 ) )
        self.assertEqual( (3.0/8.0) * 3 , self.g.expected_unmodified_hits( p2 ) )


        #p1, after rerolls
        self.assertEqual( 1, self.g.total_red_hits_after_rerolls( p1 ) )
        self.assertEqual( 1.5, self.g.expected_hits_after_rerolls( p1 ))

        #p2, after rerolls
        self.assertEqual( 1, self.g.total_red_hits_after_rerolls( p2 ) )
        self.assertEqual(  (3.0/8.0) * 5, self.g.expected_hits_after_rerolls( p2 ))

        #p1, after converts
        self.assertEqual( 2, self.g.total_red_hits_after_converts( p1 ) )
        self.assertEqual( 1.5, self.g.expected_hits_after_converts ( p1 ))

        #p2, after converts
        self.assertEqual( 1, self.g.total_red_hits_after_converts( p2 ) )
        self.assertEqual( (3.0/8.0) * 5, self.g.expected_hits_after_converts ( p2 ))


        #CRITS
        #p1, initial rolls
        self.assertEqual( 1, self.g.unmodified_crits( p1 ) )
        self.assertEqual( (1.0/8.0) * 4 , self.g.expected_unmodified_crits( p1 ) )

        #p2, initial roles
        self.assertEqual( 1, self.g.unmodified_crits( p2 ) )
        self.assertEqual( (1.0/8.0) * 3 , self.g.expected_unmodified_crits( p2 ) )


        #p1, after rerolls
        self.assertEqual( 1, self.g.total_red_crits_after_rerolls( p1 ) )
        self.assertEqual( .5, self.g.expected_crits_after_rerolls( p1 ))

        #p2, after rerolls
        self.assertEqual( 1, self.g.total_red_crits_after_rerolls( p2 ) )
        self.assertEqual(  (1.0/8.0) * 5, self.g.expected_crits_after_rerolls( p2 ))

        #p1, after converts
        self.assertEqual( 1, self.g.total_red_crits_after_converts( p1 ) )
        self.assertEqual( .5, self.g.expected_crits_after_converts ( p1 ))

        #p2, after converts
        self.assertEqual( 2, self.g.total_red_crits_after_converts( p2 ) )
        self.assertEqual( (1.0/8.0) * 5, self.g.expected_crits_after_converts ( p2 ))

        #RED FOCUS
        #p1, initial rolls
        self.assertEqual( 1, self.g.unmodified_focuses( p1 ) )
        self.assertEqual( (2.0/8.0) * 4 , self.g.expected_unmodified_focuses( p1 ) )

        #p2, initial roles
        self.assertEqual( 0, self.g.unmodified_focuses( p2 ) )
        self.assertEqual( (2.0/8.0) * 3 , self.g.expected_unmodified_focuses( p2 ) )


        #p1, after rerolls
        self.assertEqual( 1, self.g.total_red_focuses_after_rerolls( p1 ) )
        self.assertEqual( 4 * (2.0/8.0), self.g.expected_focuses_after_rerolls( p1 ))

        #p2, after rerolls
        self.assertEqual( 1, self.g.total_red_focuses_after_rerolls( p2 ) )
        self.assertEqual(  (2.0/8.0) * 5, self.g.expected_focuses_after_rerolls( p2 ))

        #p1, after converts
        self.assertEqual( 0, self.g.total_red_focuses_after_converts( p1 ) )
        self.assertEqual( (2.0/8.0) * 4, self.g.expected_focuses_after_converts ( p1 ))

        #p2, after converts
        self.assertEqual( 0, self.g.total_red_focuses_after_converts( p2 ) )
        self.assertEqual( (2.0/8.0) * 5, self.g.expected_focuses_after_converts ( p2 ))

        #RED BLANK
        #p1, initial blank rolls
        self.assertEqual( 1, self.g.unmodified_blanks( p1 ) )
        self.assertEqual( (2.0/8.0) * 4 , self.g.expected_unmodified_blanks( p1 ) )

        #p2, initial blank rolls
        self.assertEqual( 2, self.g.unmodified_blanks( p2 ) )
        self.assertEqual( (2.0/8.0) * 3 , self.g.expected_unmodified_focuses( p2 ) )


        #p1, blanks after rerolls
        self.assertEqual( 1, self.g.total_red_blanks_after_rerolls( p1 ) )
        self.assertEqual( 4 * (2.0/8.0), self.g.expected_blanks_after_rerolls( p1 ))

        #p2, after rerolls
        self.assertEqual( 2, self.g.total_red_blanks_after_rerolls( p2 ) )
        self.assertEqual(  (2.0/8.0) * 5, self.g.expected_blanks_after_rerolls( p2 ))

        #p1, after converts
        self.assertEqual( 1, self.g.total_red_blanks_after_converts( p1 ) )
        self.assertEqual( (2.0/8.0) * 4, self.g.expected_blanks_after_converts ( p1 ))

        #p2, after converts
        self.assertEqual( 2, self.g.total_red_blanks_after_converts( p2 ) )
        self.assertEqual( (2.0/8.0) * 5, self.g.expected_blanks_after_converts ( p2 ))



        #green dice
        self.assertEqual( 6, self.g.total_greens(p1))
        self.assertEqual( 4, self.g.total_greens(p2))

        #EVADES
        self.assertEqual( 0, self.g.unmodified_evades(p1))
        self.assertEqual( (3.0/8.0) * 6,  self.g.expected_unmodified_evades(p1))

        self.assertEqual( 2, self.g.unmodified_evades(p2))
        self.assertEqual( (3.0/8.0) * 4,  self.g.expected_unmodified_evades(p2))


        #p1, after rerolls
        self.assertEqual( 0, self.g.total_green_evades_after_rerolls( p1 ) )
        self.assertEqual( (3.0/8.0) * 7, self.g.expected_green_evades_after_rerolls( p1 ))

        #p2, after rerolls
        self.assertEqual( 2, self.g.total_green_evades_after_rerolls( p2 ) )
        self.assertEqual(  (3.0/8.0) * 4, self.g.expected_green_evades_after_rerolls( p2 ))

        #p1, after converts
        self.assertEqual( 4, self.g.total_green_evades_after_converts( p1 ) )
        self.assertEqual( (3.0/8.0) * 7 , self.g.expected_green_evades_after_converts ( p1 ))

        #p2, after converts
        self.assertEqual( 3, self.g.total_green_evades_after_converts( p2 ) )
        self.assertEqual( (3.0/8.0) * 4, self.g.expected_green_evades_after_converts ( p2 ))


        #GREEN FOCUSES
        self.assertEqual( 3, self.g.unmodified_green_focuses( p1 ) )
        self.assertEqual( (2.0/8.0) * 6 , self.g.expected_unmodified_green_focuses( p1 ) )

        #p2, initial roles
        self.assertEqual( 1, self.g.unmodified_green_focuses( p2 ) )
        self.assertEqual( (2.0/8.0) * 4 , self.g.expected_unmodified_green_focuses( p2 ) )


        #p1, after rerolls
        self.assertEqual( 4, self.g.total_green_focuses_after_rerolls( p1 ) )
        self.assertEqual( 7 * (2.0/8.0), self.g.expected_green_focuses_after_rerolls( p1 ))

        #p2, after rerolls
        self.assertEqual( 1, self.g.total_green_focuses_after_rerolls( p2 ) )
        self.assertEqual( (2.0/8.0) * 4, self.g.expected_green_focuses_after_rerolls( p2 ))

        #p1, after converts
        self.assertEqual( 0, self.g.total_green_focuses_after_converts( p1 ) )
        self.assertEqual( (2.0/8.0) * 7, self.g.expected_green_focuses_after_converts ( p1 ))

        #p2, after converts
        self.assertEqual( 0, self.g.total_green_focuses_after_converts( p2 ) )
        self.assertEqual( (2.0/8.0) * 4, self.g.expected_green_focuses_after_converts ( p2 ))

        #GREEN BLANKS

        self.assertEqual( 3, self.g.unmodified_green_blanks( p1 ) )
        self.assertEqual( (3.0/8.0) * 6 , self.g.expected_unmodified_green_blanks( p1 ) )

        #p2, initial roles
        self.assertEqual( 1, self.g.unmodified_green_blanks( p2 ) )
        self.assertEqual( (3.0/8.0) * 4 , self.g.expected_unmodified_green_blanks( p2 ) )


        #p1, after rerolls
        self.assertEqual( 3, self.g.total_green_blanks_after_rerolls( p1 ) )
        self.assertEqual( 7 * (3.0/8.0), self.g.expected_green_blanks_after_rerolls( p1 ))

        #p2, after rerolls
        self.assertEqual( 1, self.g.total_green_blanks_after_rerolls( p2 ) )
        self.assertEqual( (3.0/8.0) * 4, self.g.expected_green_blanks_after_rerolls( p2 ))

        #p1, after converts
        self.assertEqual( 3, self.g.total_green_blanks_after_converts( p1 ) )
        self.assertEqual( (3.0/8.0) * 7, self.g.expected_green_blanks_after_converts ( p1 ))

        #p2, after converts
        self.assertEqual( 1, self.g.total_green_blanks_after_converts( p2 ) )
        self.assertEqual( (3.0/8.0) * 4, self.g.expected_green_blanks_after_converts ( p2 ))




    def testAttackSetStats(self):

        self.assertEqual( 4, len(self.tape.attack_sets) )

        aset = self.tape.attack_sets[0]
        self.assertEqual( -.3125, aset.total_attack_end_luck() )
        self.assertEqual( .3125, aset.total_defense_end_luck() )


        aset = self.tape.attack_sets[1]
        self.assertEqual( .9375, aset.total_attack_end_luck() )
        self.assertEqual( 0.4375, aset.total_defense_end_luck() )

        aset = self.tape.attack_sets[2]
        self.assertEqual( 0.9375, aset.total_attack_end_luck() )
        self.assertEqual( 1.3125, aset.total_defense_end_luck() )


        aset = self.tape.attack_sets[3]
        self.assertEqual( 0.59375, aset.total_attack_end_luck() )
        self.assertEqual( -0.6875, aset.total_defense_end_luck() )


if __name__ == "__main__":
    unittest.main()


