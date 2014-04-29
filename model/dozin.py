import unittest
from persistence import DiceThrow, DiceThrowResult, Dice, DiceFace, DiceType

__author__ = 'lhayhurst'

#model developed by me and dom

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

    def add_roll(self, result, type):
        if type == 'Attack':
            self.total_reds += 1
            if result.is_hit():
                self.red_hits += 1
            elif result.is_crit():
                self.red_crits += 1
            elif result.get_result() == 'Focus':
                self.red_eyes += 1
            elif result.get_result() == 'Blank':
                self.red_blanks += 1
            else:
                RuntimeError ("unknown dice type, wtf?!")
        elif type == 'Defend':
            self.total_greens += 1
            if result.get_result() == 'Evade':
                self.green_evades += 1
            elif result.get_result() == 'Focus':
                self.green_eyes += 1
            elif result.get_result() == 'Blank':
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

class DozinModel:

    def __init__(self, player):
        self.dice_stats = DiceStats(player)
        self.player     = player
        self.red_luck = []
        self.green_luck = []
        self.green_luck.append(0)
        self.red_luck.append(0)
        self.red_turns = []
        self.green_turns = []

    def add_throw(self):
        self.red_turns.append( self.red_luck[-1] )
        self.green_turns.append( self.green_luck[-1])


    def add_defense_luck_record(self):

        exp_evades         = self.dice_stats.expected_green_evades()
        evade_dev          = self.dice_stats.green_evades - exp_evades
        weighted_evade_dev = evade_dev * DiceStats.EVADE_WEIGHT

        exp_focus          = self.dice_stats.expected_green_eyes()
        focus_dev          = self.dice_stats.green_eyes - exp_focus
        weighted_focus_dev = focus_dev * DiceStats.GREEN_EYE_WEIGHT

        exp_blank          = self.dice_stats.expected_green_blanks()
        blank_dev          = self.dice_stats.green_blanks - exp_blank
        weighted_blank_dev = blank_dev * DiceStats.GREEN_BLANK_WEIGHT

        luck = weighted_evade_dev + weighted_focus_dev + weighted_blank_dev

        self.green_luck.append(luck)

    def add_attack_luck_record(self):

        exp_hits         = self.dice_stats.expected_red_hits()
        hit_dev          = self.dice_stats.red_hits - exp_hits
        weighted_hit_dev = hit_dev * DiceStats.HIT_WEIGHT

        exp_crits         = self.dice_stats.expected_red_crits()
        crit_dev          = self.dice_stats.red_crits - exp_crits
        weighted_crit_dev = crit_dev * DiceStats.CRIT_WEIGHT

        exp_focus          = self.dice_stats.expected_red_eyes()
        focus_dev          = self.dice_stats.red_eyes - exp_focus
        weighted_focus_dev = focus_dev * DiceStats.RED_EYE_WEIGHT

        exp_blank          = self.dice_stats.expected_red_misses()
        blank_dev          = self.dice_stats.red_blanks - exp_blank
        weighted_blank_dev = blank_dev * DiceStats.RED_BLANK_WEIGHT

        luck = weighted_hit_dev + weighted_crit_dev + weighted_focus_dev + weighted_blank_dev

        self.red_luck.append(luck)

    def add_roll(self, result, type):
        self.dice_stats.add_roll(result, type)

    def add_dice_set(self, throw):

        for result in throw.results:
            self.dice_stats.add_roll( result, 'Attack')
            self.add_attack_luck_record()
        for result in throw.defense_rolls:
            self.dice_stats.add_roll( result, 'Defend')
            self.add_defense_luck_record()


    def last_attack_set_red_luck(self):
        return self.red_luck[-1]

    def last_attack_set_green_luck(self):
        return self.green_luck[-1]


class TestStats(unittest.TestCase):

    def test_greens(self):

        t = DiceThrow()

        r1 = DiceThrowResult()
        r1.dice = Dice()
        r1.dice.dice_face = DiceFace.EVADE
        r1.dice.dice_face = DiceType.GREEN
        t.results.append(r1)
        t.results.append(r1)
        t.results.append(r1)
        t.results.append(r1)
        t.results.append(r1)
        t.results.append(r1)

        stats = DozinModel("P1")
        stats.add_dice_set(1, t)
        stats.add_defense_luck_record()
        stats.add_throw()
        self.assertEqual( stats.last_attack_set_green_luck(), 3.375)

        t = AttackSet("P1", "P2")
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 1, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 2, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 3, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 4, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 5, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 6, "P1" ))

        stats.add_dice_set(2, t)
        stats.add_defense_luck_record()
        stats.add_throw()
        self.assertEqual( stats.last_attack_set_green_luck(), 2.25)

        t = AttackSet("P1", "P2")
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 1, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 2, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 3, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 4, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 5, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 6, "P1" ))

        stats.add_dice_set(3, t)
        stats.add_defense_luck_record()
        stats.add_throw()
        self.assertEqual( stats.last_attack_set_green_luck(), -0.375)

        t = AttackSet("P1", "P2")
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 1, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 2, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 3, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.FOCUS, 4, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 5, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.BLANK, 6, "P1" ))

        stats.add_dice_set(4, t)
        stats.add_defense_luck_record()
        stats.add_throw()
        self.assertEqual( stats.last_attack_set_green_luck(), -0.5)


if __name__ == "__main__":
    unittest.main()


