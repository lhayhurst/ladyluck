import unittest
import myapp
from parser import LogFileParser
from persistence import DiceThrowType, DiceFace, Dice, DiceThrowAdjustmentType


class TestFsm(unittest.TestCase):



    #@unittest.skip("school")
    def test_add_evade(self):
        session = myapp.db_connector.get_session()
        parser = LogFileParser(session)
        parser.add_line("* *** sozin Rolls to Attack: [Blank] ***")
        parser.add_line("* *** tal Rolls to Defend: [Blank], [Blank], [Focus], [], [], [], [] ***")
        parser.add_line("* *** tal Re-Rolls Defense Die 1 (Blank) and gets a [Focus] ***")
        parser.add_line("* *** tal Re-Rolls Defense Die 2 (Blank) and gets a [Focus] ***")
        parser.add_line("* *** sozin used Focus on Defense Dice ***")
        parser.add_line("* *** tal added an Evade ***")
        parser.run_finite_state_machine()

        gt = parser.game_tape
        self.assertEqual( 2, len(gt))
        attack_throw = gt[0]
        self.assertEqual( "sozin", attack_throw.player.name)
        self.assertEqual( 1, attack_throw.attack_set_num)
        self.assertEqual( attack_throw.throw_type, DiceThrowType.ATTACK)
        results = attack_throw.results
        self.assertEqual( 1, len(results))

        defense_throw = gt[1]
        self.assertEqual( "tal", defense_throw.player.name)
        self.assertEqual( 1, defense_throw.attack_set_num)
        self.assertEqual( defense_throw.throw_type, DiceThrowType.DEFEND)
        results = defense_throw.results
        self.assertEqual( 4, len(results))

        d1 = results[0]
        self.assertEqual( DiceFace.EVADE, d1.final_dice.dice_face )
        self.assertEqual( Dice.ROLLED, d1.final_dice.dice_origination)
        d2 = results[1]
        self.assertEqual( DiceFace.EVADE, d2.final_dice.dice_face)
        self.assertEqual( Dice.ROLLED, d2.final_dice.dice_origination)
        d3 = results[2]
        self.assertEqual( DiceFace.EVADE, d3.final_dice.dice_face)
        self.assertEqual( Dice.ROLLED, d3.final_dice.dice_origination)
        d4 = results[3]
        self.assertEqual( DiceFace.EVADE, d4.final_dice.dice_face)
        self.assertEqual( Dice.ADDED, d4.final_dice.dice_origination)


    def test_cancel(self):
        session = myapp.db_connector.get_session()
        parser = LogFileParser(session)
        parser.add_line("* *** sozin Rolls to Attack: [Crit], [Hit], [Hit], [], [], [] ***")
        parser.add_line("* *** tal cancelled a Hit ***")
        parser.add_line("* *** tal cancelled a Hit ***")
        parser.run_finite_state_machine()
        gt = parser.game_tape
        throw = gt[0]
        results = throw.results
        self.assertEqual( 3, len(results))

        d1 = results[0]
        self.assertEqual( DiceFace.CRIT, d1.final_dice.dice_face )
        self.assertEqual( Dice.ROLLED, d1.final_dice.dice_origination)
        d2 = results[1]
        self.assertEqual( DiceFace.HIT, d2.final_dice.dice_face)
        self.assertEqual( 1, len(d2.adjustments))
        adj = d2.adjustments[0]
        self.assertEqual(DiceThrowAdjustmentType.CANCELLED, adj.adjustment_type)
        d3 = results[2]
        self.assertEqual( DiceFace.HIT, d3.final_dice.dice_face)
        self.assertEqual( Dice.ROLLED, d3.final_dice.dice_origination)
        adj = d3.adjustments[0]
        self.assertEqual(DiceThrowAdjustmentType.CANCELLED, adj.adjustment_type)


    def test_attack_roll_focus_reroll_turn(self):
        session = myapp.db_connector.get_session()
        parser = LogFileParser(session)
        parser.add_line("* *** sozin Rolls to Attack: [Blank], [Blank], [Blank], [], [], [] ***")
        parser.add_line("* *** sozin turns Attack Die 1 [Blank] into a [Hit] ***")
        parser.add_line("* *** sozin turns Attack Die 2 [Blank] into a [Focus] ***")
        parser.add_line("* *** sozin Re-Rolls Attack Die 3 [Blank] and gets a [Focus] ***")
        parser.add_line("* *** sozin used Focus on Attack Dice ***")
        parser.add_line("* *** sozin added a Crit ***")

        parser.run_finite_state_machine()
        gt = parser.game_tape
        throw = gt[0]
        results = throw.results
        self.assertEqual( 4, len(results))

        d1 = results[0]
        self.assertEqual( DiceFace.HIT, d1.final_dice.dice_face )
        self.assertEqual( Dice.ROLLED, d1.final_dice.dice_origination)
        d2 = results[1]
        self.assertEqual( DiceFace.HIT, d2.final_dice.dice_face)
        self.assertEqual( Dice.ROLLED, d2.final_dice.dice_origination)
        d3 = results[2]
        self.assertEqual( DiceFace.HIT, d3.final_dice.dice_face)
        self.assertEqual( Dice.ROLLED, d3.final_dice.dice_origination)
        d4 = results[3]
        self.assertEqual( DiceFace.CRIT, d4.final_dice.dice_face)
        self.assertEqual( Dice.ADDED, d4.final_dice.dice_origination)


    #@unittest.skip("school")
    def test_basic_add_attack_dice_three(self):
        session = myapp.db_connector.get_session()
        parser = LogFileParser(session)
        parser.add_line("* *** sozin Rolls to Attack: [Blank] ***")
        parser.add_line("* *** sozin added a Crit ***")
        parser.add_line("* *** sozin added a Hit ***")
        parser.add_line("* *** sozin added a Hit ***")

        parser.run_finite_state_machine()

        gt = parser.game_tape
        throw = gt[0]
        self.assertEqual( "sozin", throw.player.name)
        self.assertEqual( 1, throw.attack_set_num)
        self.assertEqual( throw.throw_type, DiceThrowType.ATTACK)
        results = throw.results
        self.assertEqual( 4, len(results))

        d1 = results[0]
        self.assertEqual( DiceFace.BLANK, d1.final_dice.dice_face )
        self.assertEqual( Dice.ROLLED, d1.final_dice.dice_origination)
        d2 = results[1]
        self.assertEqual( DiceFace.CRIT, d2.final_dice.dice_face)
        self.assertEqual( Dice.ADDED, d2.final_dice.dice_origination)

        d3 = results[2]
        self.assertEqual( DiceFace.HIT, d3.final_dice.dice_face)
        self.assertEqual( Dice.ADDED, d3.final_dice.dice_origination)

        d4 = results[3]
        self.assertEqual( DiceFace.HIT, d4.final_dice.dice_face)
        self.assertEqual( Dice.ADDED, d4.final_dice.dice_origination)

    #@unittest.skip("school")
    def test_basic_add_attack_dice_two(self):
        session = myapp.db_connector.get_session()
        parser = LogFileParser(session)
        parser.add_line("* *** sozin Rolls to Attack: [Blank], [Blank], [Blank], [], [], [] ***")
        parser.add_line("* *** sozin added a Crit ***")
        parser.add_line("* *** sozin Re-Rolls Attack Die 1 [Blank] and gets a [Focus] ***")
        parser.add_line("* *** sozin Re-Rolls Attack Die 2 [Blank] and gets a [Crit] ***")
        parser.add_line("* *** sozin Re-Rolls Attack Die 3 [Blank] and gets a [Focus] ***")
        parser.add_line("* *** sozin used Focus on Attack Dice ***")
        parser.run_finite_state_machine()

        gt = parser.game_tape
        throw = gt[0]
        self.assertEqual( "sozin", throw.player.name)
        self.assertEqual( 1, throw.attack_set_num)
        self.assertEqual( throw.throw_type, DiceThrowType.ATTACK)
        results = throw.results
        self.assertEqual( 4, len(results))

        d1 = results[0]
        self.assertEqual( DiceFace.HIT, d1.final_dice.dice_face )
        d2 = results[1]
        self.assertEqual( DiceFace.CRIT, d2.final_dice.dice_face)
        d3 = results[2]
        self.assertEqual( DiceFace.HIT, d3.final_dice.dice_face)
        d4 = results[3]
        self.assertEqual( DiceFace.CRIT, d4.final_dice.dice_face)

    #@unittest.skip("school")
    def test_basic_add_attack_dice(self):
        session = myapp.db_connector.get_session()
        parser = LogFileParser(session)
        parser.add_line("* *** sozin Rolls to Attack: [Hit], [Focus], [Blank], [], [], [], [] ***")
        parser.add_line("* *** sozin added a Crit ***")
        parser.add_line("* *** sozin Re-Rolls Attack Die 3 [Blank] and gets a [Focus] ***")
        parser.add_line("* *** sozin used Focus on Attack Dice ***")
        parser.run_finite_state_machine()

        gt = parser.game_tape
        throw = gt[0]
        self.assertEqual( "sozin", throw.player.name)
        self.assertEqual( 1, throw.attack_set_num)
        self.assertEqual( throw.throw_type, DiceThrowType.ATTACK)
        results = throw.results
        self.assertEqual( 4, len(results))

        d1 = results[0]
        self.assertEqual( DiceFace.HIT, d1.final_dice.dice_face )
        d2 = results[1]
        self.assertEqual( DiceFace.HIT, d2.final_dice.dice_face)
        d3 = results[2]
        self.assertEqual( DiceFace.HIT, d3.final_dice.dice_face)
        d4 = results[3]
        self.assertEqual( DiceFace.CRIT, d4.final_dice.dice_face)

if __name__ == "__main__":
    unittest.main()