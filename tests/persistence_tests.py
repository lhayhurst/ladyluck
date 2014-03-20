import sys

__author__ = 'lhayhurst'

from parser import LogFileParser
from persistence import Dice, DiceType, DiceFace, Player, Game, GameRoll, GameRollType, PersistenceManager
import unittest



class TestPersistence(unittest.TestCase):

    def setUp(self):
        self.persistence_manager = PersistenceManager()

        #just keep a top level reference to these guys for ease of use
        self.engine = self.persistence_manager.engine
        self.connection = self.persistence_manager.connection
        self.session = self.persistence_manager.session

        #and then create the database schema, reference tables
        self.persistence_manager.create_schema()
        self.persistence_manager.populate_reference_tables()
        self.session.commit()

    def tearDown(self):

        self.session.close_all()
        self.persistence_manager.drop_schema()

    #@unittest.skip("because")
    def testDice(self):

        red_dice = self.session.query(Dice).filter_by(dice_type=DiceType.RED).all()
        self.assertEqual( red_dice[0].dice_face, DiceFace.HIT )
        self.assertEqual( red_dice[1].dice_face, DiceFace.CRIT )
        self.assertEqual( red_dice[2].dice_face, DiceFace.FOCUS )
        self.assertEqual( red_dice[3].dice_face, DiceFace.BLANK )

        for dice in red_dice:
            self.assertEqual( dice.dice_type, DiceType.RED)

        green_dice = self.session.query(Dice).filter_by(dice_type=DiceType.GREEN).all()
        self.assertEqual( green_dice[0].dice_face, DiceFace.EVADE )
        self.assertEqual( green_dice[1].dice_face, DiceFace.FOCUS )
        self.assertEqual( green_dice[2].dice_face, DiceFace.BLANK )

        for dice in green_dice:
            self.assertEqual( dice.dice_type, DiceType.GREEN)

    #@unittest.skip("because")
    def testTape(self):
        parser = LogFileParser()
        parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()
        game_tape = parser.game_tape.tape
        p1 = Player(name=parser.game_tape.player1)
        p2 = Player(name=parser.game_tape.player2)
        g = Game(p1, p2)

        session = self.session
        session.add(g)
        session.commit()

        for gt in game_tape:
            player_id = None
            if gt.player == p1.name:
                player_id = p1.id
            elif gt.player == p2.name:
                player_id = p2.id
            else:
                self.fail("unknown player detected")
            game_id = g.id
            dice = self.session.query(Dice).filter_by(dice_type=gt.dice_type, dice_face=gt.dice_face).first()

            roll = GameRoll( player_id=player_id,
                                 game_id=game_id,
                                 roll_type=gt.entry_type,
                                 dice_id=dice.id,
                                 attack_set_num=gt.attack_set_number,
                                 dice_num=gt.dice_num )
            session.add(roll)
        session.commit()

        #now get 'em back
        my_g = self.session.query(Game).filter_by(id=g.id).first()
        self.assertTrue( g is not None )

        my_game_roll = my_g.game_roll
        self.assertTrue( my_game_roll is not None)
        self.assertEqual( len(my_game_roll) , 24 )

        #* *** Ryan Krippendorf Rolls to Attack: [Focus], [Blank], [], [], [], [], [] ***
        entry = my_game_roll[0]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p1.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE, entry.roll_type)
        self.assertEqual( 1, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.FOCUS, entry.dice.dice_face)

        entry = my_game_roll[1]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p1.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE, entry.roll_type)
        self.assertEqual( 1, entry.attack_set_num)
        self.assertEqual( 2, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, entry.dice.dice_face)

        #* *** Ryan Krippendorf turns Attack Die 1 (Focus) into a [Hit] ***
        entry = my_game_roll[2]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p1.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE_MODIFICATION, entry.roll_type)
        self.assertEqual( 1, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.HIT, entry.dice.dice_face)

        #* *** sozin Rolls to Defend: [Evade], [Blank], [Evade], [], [], [], [] ***
        entry = my_game_roll[3]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.DEFENSE_DICE, entry.roll_type)
        self.assertEqual( 1, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.GREEN, entry.dice.dice_type)
        self.assertEqual( DiceFace.EVADE, entry.dice.dice_face)

        entry = my_game_roll[4]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.DEFENSE_DICE, entry.roll_type)
        self.assertEqual( 1, entry.attack_set_num)
        self.assertEqual( 2, entry.dice_num)
        self.assertEqual( DiceType.GREEN, entry.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, entry.dice.dice_face)

        entry = my_game_roll[5]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.DEFENSE_DICE, entry.roll_type)
        self.assertEqual( 1, entry.attack_set_num)
        self.assertEqual( 3, entry.dice_num)
        self.assertEqual( DiceType.GREEN, entry.dice.dice_type)
        self.assertEqual( DiceFace.EVADE, entry.dice.dice_face)

        #* *** Ryan Krippendorf Rolls to Attack: [Hit], [Crit], [], [], [], [], [] ***
        entry = my_game_roll[6]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p1.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE, entry.roll_type)
        self.assertEqual( 2, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.HIT, entry.dice.dice_face)

        entry = my_game_roll[7]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p1.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE, entry.roll_type)
        self.assertEqual( 2, entry.attack_set_num)
        self.assertEqual( 2, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.CRIT, entry.dice.dice_face)

        #* *** sozin Rolls to Defend: [Focus], [], [], [], [], [], [] ***
        entry = my_game_roll[8]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.DEFENSE_DICE, entry.roll_type)
        self.assertEqual( 2, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.GREEN, entry.dice.dice_type)
        self.assertEqual( DiceFace.FOCUS, entry.dice.dice_face)

        #* *** sozin turns Defense Die 1 (Focus) into a [Evade] ***
        entry = my_game_roll[9]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.DEFENSE_DICE_MODIFICATION, entry.roll_type)
        self.assertEqual( 2, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.GREEN, entry.dice.dice_type)
        self.assertEqual( DiceFace.EVADE, entry.dice.dice_face)

        #* *** sozin Rolls to Attack: [Blank], [Blank], [], [], [], [], [] ***
        entry = my_game_roll[10]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE, entry.roll_type)
        self.assertEqual( 3, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, entry.dice.dice_face)

        entry = my_game_roll[11]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE, entry.roll_type)
        self.assertEqual( 3, entry.attack_set_num)
        self.assertEqual( 2, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, entry.dice.dice_face)

        #* *** sozin Re-Rolls Attack Die 1 [Focus] and gets a [Hit] ***
        entry = my_game_roll[12]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE_REROLL, entry.roll_type)
        self.assertEqual( 3, entry.attack_set_num)
        self.assertEqual( 1, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.HIT, entry.dice.dice_face)

        #* *** sozin Re-Rolls Attack Die 2 [Focus] and gets a [Focus] ***
        entry = my_game_roll[13]
        self.assertEqual( g.id, entry.game_id)
        self.assertEqual( p2.name, entry.player.name)
        self.assertEqual( GameRollType.ATTACK_DICE_REROLL, entry.roll_type)
        self.assertEqual( 3, entry.attack_set_num)
        self.assertEqual( 2, entry.dice_num)
        self.assertEqual( DiceType.RED, entry.dice.dice_type)
        self.assertEqual( DiceFace.FOCUS, entry.dice.dice_face)

    #@unittest.skip("because")
    def testGameWithPlayer(self):
        parser = LogFileParser()
        parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()
        game_tape = parser.game_tape
        p1 = Player(name=game_tape.player1)
        p2 = Player(name=game_tape.player2)
        g = Game(p1, p2, winner=p1)


        session = self.session
        session.add(g)
        session.commit()


        my_g = session.query(Game).filter_by(game_name=g.game_name).first()
        self.assertTrue( my_g is not None)
        self.assertEqual( g.game_name, my_g.game_name)
        self.assertTrue( len(g.game_players) == 2 )
        self.assertTrue( g.game_players[0].name == "Ryan Krippendorf")
        self.assertTrue( g.game_players[1].name == "sozin")
        self.assertTrue( g.game_winner is not None)
        self.assertTrue( g.game_winner.name == "Ryan Krippendorf")


        my_player1 =    session.query(Player).filter_by(name=p1.name).first()
        self.assertEqual("Ryan Krippendorf", my_player1.name)
        self.assertTrue( my_player1.id == g.game_players[0].id)

        my_player2 =    session.query(Player).filter_by(name=p2.name).first()
        self.assertEqual("sozin", my_player2.name)
        self.assertTrue( my_player2.id == g.game_players[1].id )

        #change the name of something and verify that the id remains the game
        p1.name = "Darth Vader"
        session.add(p1)
        session.commit()

        vader = session.query(Player).filter_by(name=p1.name).first()
        self.assertEqual( my_player1.id, vader.id )


if __name__ == "__main__":
    if len (sys.argv) == 1:
        unittest.main()
    elif sys.argv[1] == 'create':
        pm = PersistenceManager(True)
        pm.create_schema()
        pm.populate_reference_tables()
        pm.session.commit()
        pm.session.close_all()
    elif sys.argv[1] == 'destroy':
        pm = PersistenceManager(True)
        pm.drop_schema()
        pm.session.commit()
        pm.session.close_all()