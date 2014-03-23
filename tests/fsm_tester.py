import os
import unittest
import sqlalchemy
from model import DiceRoll
from parser import LogFileParser

class TestFsm(unittest.TestCase):
    @unittest.skip("demonstrating skipping")
    def test_fsm(self):
        parser = LogFileParser()
        parser.read_input_from_file("logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()
        roll_sets = parser.get_roll_sets()
        self.assertEqual( len(roll_sets), 4)

        rs = roll_sets[0]
        self.assertEqual( rs.attacking_player, "Ryan Krippendorf")
        self.assertEqual( rs.defending_player, "sozin")
        self.assertEqual( len(rs.attack_rolls), 2 )
        self.assertEqual( len(rs.defense_rolls), 3 )


        roll = rs.attack_rolls[0]
        self.assertEqual( roll.player, "Ryan Krippendorf")
        self.assertTrue( roll.was_modified() )
        self.assertEqual( "Focus", roll.started_out_as() )
        self.assertEqual( roll.get_result(), "Hit")
        self.assertEqual( roll.num, 1 )

        roll = rs.attack_rolls[1]
        self.assertEqual( roll.player, "Ryan Krippendorf")
        self.assertEqual( roll.get_result(), "Blank")
        self.assertEqual( roll.num, 2 )

        roll = rs.defense_rolls[0]
        self.assertEqual( roll.player, "sozin")
        self.assertEqual( roll.get_result(), "Evade")
        self.assertEqual( roll.num, 1 )

        roll = rs.defense_rolls[1]
        self.assertEqual( roll.player, "sozin")
        self.assertEqual( roll.get_result(), "Blank")
        self.assertEqual( roll.num, 2 )

        roll = rs.defense_rolls[2]
        self.assertEqual( roll.player, "sozin")
        self.assertEqual( roll.get_result(), "Evade")
        self.assertEqual( roll.num, 3 )

        rs = roll_sets[1]
        self.assertEqual( rs.attacking_player, "Ryan Krippendorf")
        self.assertEqual( rs.defending_player, "sozin")
        self.assertEqual( len(rs.attack_rolls), 2 )
        self.assertEqual( len(rs.defense_rolls), 1 )


        roll = rs.attack_rolls[0]
        self.assertEqual( roll.player, "Ryan Krippendorf")
        self.assertEqual( roll.get_result(), "Hit")
        self.assertEqual( roll.num, 1 )

        roll = rs.attack_rolls[1]
        self.assertEqual( roll.player, "Ryan Krippendorf")
        self.assertEqual( roll.get_result(), "Crit")
        self.assertEqual( roll.num, 2 )

        roll = rs.defense_rolls[0]
        self.assertEqual( roll.player, "sozin")
        self.assertTrue( roll.was_modified())
        self.assertEqual( "Focus", roll.started_out_as())
        self.assertEqual( roll.get_result(), "Evade")
        self.assertEqual( roll.num, 1 )

        rs = roll_sets[2]
        self.assertEqual( rs.attacking_player, "sozin")
        self.assertEqual( rs.defending_player, "Ryan Krippendorf")
        self.assertEqual( len(rs.attack_rolls), 2 )
        self.assertEqual( len(rs.defense_rolls), 3 )

        roll = rs.attack_rolls[0]
        self.assertEqual( roll.player, "sozin")
        self.assertEqual( roll.get_result(), "Hit")
        self.assertTrue( roll.was_modified())
        self.assertEqual( "Blank", roll.started_out_as())
        self.assertEqual( roll.num, 1 )

        roll = rs.attack_rolls[1]
        self.assertEqual( roll.player, "sozin")
        self.assertEqual( roll.get_result(), "Focus")
        self.assertTrue( roll.was_modified())
        self.assertEqual( "Blank", roll.started_out_as() )
        self.assertEqual( roll.num, 2 )

        roll = rs.defense_rolls[0]
        self.assertEqual( roll.player, "Ryan Krippendorf")
        self.assertEqual( roll.get_result(), "Evade")
        self.assertTrue( roll.was_modified())
        self.assertEqual( "Focus", roll.started_out_as() )
        self.assertEqual( roll.num, 1 )

        roll = rs.defense_rolls[1]
        self.assertEqual( roll.player, "Ryan Krippendorf")
        self.assertEqual( roll.get_result(), "Blank")
        self.assertTrue( not roll.was_modified())
        self.assertEqual( roll.num, 2 )

        roll = rs.defense_rolls[2]
        self.assertEqual( roll.player, "Ryan Krippendorf")
        self.assertEqual( roll.get_result(), "Evade")
        self.assertTrue( roll.was_modified())
        self.assertEqual( "Focus", roll.started_out_as() )
        self.assertEqual( roll.num, 3 )

        rs = roll_sets[3]
        self.assertEqual( rs.attacking_player, "sozin")
        self.assertEqual( rs.defending_player, "Ryan Krippendorf")
        self.assertEqual( len(rs.attack_rolls), 1 )
        self.assertEqual( len(rs.defense_rolls), 3  )


        roll = rs.attack_rolls[0]
        self.assertEqual( roll.player, "sozin")
        self.assertEqual( roll.get_result(), "Crit")
        self.assertEqual( roll.num, 1 )

    def test_mu0n_v_paul_game(self):
        parser = LogFileParser()
        parser.read_input_from_file("logfiles/ricky_v_val.txt")
        parser.run_finite_state_machine()

    def test_game_tape(self):
        parser = LogFileParser()
        parser.read_input_from_file("logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()
        game_tape = parser.game_tape

        self.assertEqual( 24, len(game_tape) )

        ge = game_tape.tape[ 0 ]
        self.assertEqual( LogFileParser.PLAYER_ATTACKING, ge.game_state)
        self.assertEqual( 1, ge.attack_set_number)
        self.assertEqual( "Ryan Krippendorf", ge.player)
        self.assertEqual( GameTapeEntryType.ATTACK_DICE, ge.entry_type)
        self.assertEqual(1, ge.dice_number)
        self.assertEqual( DiceRoll.FOCUS, ge.dice_value)

        ge = game_tape.tape[ 1 ]
        self.assertEqual( LogFileParser.PLAYER_ATTACKING, ge.game_state)
        self.assertEqual( 1, ge.attack_set_number)
        self.assertEqual( "Ryan Krippendorf", ge.player)
        self.assertEqual( GameTapeEntryType.ATTACK_DICE, ge.entry_type)
        self.assertEqual(2, ge.dice_number)
        self.assertEqual( DiceRoll.BLANK, ge.dice_value)


        ge = game_tape.tape[ 2 ]
        self.assertEqual( LogFileParser.PLAYER_MODIFYING_ATTACK_DICE, ge.game_state)
        self.assertEqual( 1, ge.attack_set_number)
        self.assertEqual( "Ryan Krippendorf", ge.player)
        self.assertEqual( GameTapeEntryType.ATTACK_DICE_MODIFICATION, ge.entry_type)
        self.assertEqual(1, ge.dice_number)
        self.assertEqual( DiceRoll.HIT, ge.dice_value)

        ge = game_tape.tape[ 3 ]
        self.assertEqual( LogFileParser.PLAYER_DEFENDING, ge.game_state)
        self.assertEqual( 1, ge.attack_set_number)
        self.assertEqual( "sozin", ge.player)
        self.assertEqual( GameTapeEntryType.DEFENSE_DICE, ge.entry_type)
        self.assertEqual(1, ge.dice_number)
        self.assertEqual( DiceRoll.EVADE, ge.dice_value)

        ge = game_tape.tape[ 4 ]
        self.assertEqual( LogFileParser.PLAYER_DEFENDING, ge.game_state)
        self.assertEqual( 1, ge.attack_set_number)
        self.assertEqual( "sozin", ge.player)
        self.assertEqual( GameTapeEntryType.DEFENSE_DICE, ge.entry_type)
        self.assertEqual(2, ge.dice_number)
        self.assertEqual( DiceRoll.BLANK, ge.dice_value)

        #skip ahead a bit to look for interesting cases
        ge = game_tape.tape[ 6 ]
        self.assertEqual( LogFileParser.PLAYER_ATTACKING, ge.game_state)
        self.assertEqual( 2, ge.attack_set_number)
        self.assertEqual( "Ryan Krippendorf", ge.player)
        self.assertEqual( GameTapeEntryType.ATTACK_DICE, ge.entry_type)
        self.assertEqual(1, ge.dice_number)
        self.assertEqual( DiceRoll.HIT, ge.dice_value)

        ge = game_tape.tape[ 8 ]
        self.assertEqual( LogFileParser.PLAYER_DEFENDING, ge.game_state)
        self.assertEqual( 2, ge.attack_set_number)
        self.assertEqual( "sozin", ge.player)
        self.assertEqual( GameTapeEntryType.DEFENSE_DICE, ge.entry_type)
        self.assertEqual(1, ge.dice_number)
        self.assertEqual( DiceRoll.FOCUS, ge.dice_value)

        ge = game_tape.tape[ 9 ]
        self.assertEqual( LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE, ge.game_state)
        self.assertEqual( 2, ge.attack_set_number)
        self.assertEqual( "sozin", ge.player)
        self.assertEqual( GameTapeEntryType.DEFENSE_DICE_MODIFICATION, ge.entry_type)
        self.assertEqual(1, ge.dice_number)
        self.assertEqual( DiceRoll.EVADE, ge.dice_value)




if __name__ == "__main__":
    unittest.main()