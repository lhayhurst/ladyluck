import re
import unittest
from model import DiceRoll, AttackSet, LuckStats


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
        stats.add_throw()
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
        stats.add_throw()
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
        stats.add_throw()
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
        stats.add_throw()
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
        stats.add_throw()
        self.assertEqual( stats.last_attack_set_red_luck(), 1)

if __name__ == "__main__":
    unittest.main()
