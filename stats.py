import re
import unittest
from model import DiceRoll, AttackSet


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

        self.green_luck   = []
        self.red_luck     = []

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



    HIT_WEIGHT = 1.0
    CRIT_WEIGHT = 1.25
    RED_EYE_WEIGHT = .5
    RED_BLANK_WEIGHT = 0

    EVADE_WEIGHT = 1
    GREEN_EYE_WEIGHT = 0.75
    GREEN_BLANK_WEIGHT = 0


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

    def sub(self, from_text, to_text, text ):
        text = re.sub( from_text, to_text, text, re.M)
        return text


class LuckStats:

    def __init__(self, player):
        self.dice_stats = DiceStats(player)
        self.player     = player
        self.red_luck = []
        self.green_luck = []
        self.green_luck.append(0)
        self.red_luck.append(0)
        self.red_turns = []
        self.green_turns = []

    def add_attack_set_luck(self):
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

    def add_dice_set(self, set_num, set):

        for roll in set.attack_rolls:
            self.dice_stats.add_roll( roll, 'Attack')
            self.add_attack_luck_record()
        for roll in set.defense_rolls:
            self.dice_stats.add_roll( roll, 'Defend')
            self.add_defense_luck_record()


    def last_attack_set_red_luck(self):
        return self.red_luck[-1]

    def last_attack_set_green_luck(self):
        return self.green_luck[-1]


class TestStats(unittest.TestCase):

    def test_greens(self):
        t = AttackSet("P1", "P2")
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 1, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 2, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 3, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 4, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 5, "P1" ))
        t.add_defense_roll(DiceRoll( DiceRoll.EVADE, 6, "P1" ))

        stats = LuckStats("P1")
        stats.add_dice_set(1, t)
        stats.add_defense_luck_record()
        stats.add_attack_set_luck()
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
        stats.add_attack_set_luck()
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
        stats.add_attack_set_luck()
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
        stats.add_attack_set_luck()
        self.assertEqual( stats.last_attack_set_green_luck(), -0.5)


    def test_reds(self):
        t = AttackSet("P1", "P2")
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 1, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 2, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 3, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 4, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 5, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 6, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 7, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 8, "P1" ))

        stats = LuckStats("P1")
        stats.add_dice_set(1, t)
        stats.add_attack_luck_record()
        stats.add_attack_set_luck()
        self.assertEqual( stats.last_attack_set_red_luck(), 0)

        t = AttackSet("P1", "P2")
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 1, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 2, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 3, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 4, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 5, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 6, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 7, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.HIT, 8, "P1" ))

        stats.add_dice_set(2, t)
        stats.add_attack_luck_record()
        stats.add_attack_set_luck()
        self.assertEqual( stats.last_attack_set_red_luck(), 2.75)

        t = AttackSet("P1", "P2")
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 1, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 2, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 3, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 4, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 5, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 6, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 7, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.CRIT, 8, "P1" ))

        stats.add_dice_set(3, t)
        stats.add_attack_luck_record()
        stats.add_attack_set_luck()
        self.assertEqual( stats.last_attack_set_red_luck(), 7.5)

        t = AttackSet("P1", "P2")
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 1, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 2, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 3, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 4, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 5, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 6, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 7, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.FOCUS, 8, "P1" ))

        stats.add_dice_set(4, t)
        stats.add_attack_luck_record()
        stats.add_attack_set_luck()
        self.assertEqual( stats.last_attack_set_red_luck(), 6.25)

        t = AttackSet("P1", "P2")
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 1, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 2, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 3, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 4, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 5, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 6, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 7, "P1" ))
        t.add_attack_roll(DiceRoll( DiceRoll.BLANK, 8, "P1" ))

        stats.add_dice_set(5, t)
        stats.add_attack_luck_record()
        stats.add_attack_set_luck()
        self.assertEqual( stats.last_attack_set_red_luck(), 1)

if __name__ == "__main__":
    unittest.main()
