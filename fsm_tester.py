

import unittest
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
        parser.read_input_from_file("logfiles/muon_v_paul.txt")
        parser.run_finite_state_machine()


if __name__ == "__main__":
    unittest.main()