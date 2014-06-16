from myapp import db_connector
import myapp

__author__ = 'lhayhurst'
import sys
from parser import LogFileParser
from persistence import Dice, DiceType, DiceFace, Player, Game, PersistenceManager, DiceThrowType, \
    DiceThrowAdjustmentType
import unittest


class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        self.persistence_manager = PersistenceManager(True)

        #just keep a top level reference to these guys for ease of use
        self.session = db_connector.get_session()

        #and then create the database schema, reference tables
        self.persistence_manager.create_schema()
        self.persistence_manager.populate_reference_tables()
        self.session.commit()

    def tearDown(self):

#        self.session.flush()
        self.session.close_all()
        self.persistence_manager.drop_schema()


class TestPersistence(DatabaseTestCase):

    #@unittest.skip("because")
    def testSchemaConstruction(self):
        self.assertTrue(True)

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


#    @unittest.skip("because")
    def testDoubleGameLoadPlayersRemainTheSame(self):

        parser = LogFileParser(self.session)
        parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()

        g = Game(self.session, parser.get_players())

        p1 = g.game_players[0]
        p2 = g.game_players[1]
        g.game_winner = p1


        session = self.session
        session.add(g)
        session.commit()

        parser = LogFileParser(self.session)
        parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()

        g = Game(self.session, parser.get_players())

        session.add(g)
        session.commit()

        p1a = g.game_players[0]
        p2a = g.game_players[1]

        g.game_winner = p1a

        session = self.session
        session.add (g)
        session.commit()

        self.assertTrue( p1.id == p1a.id)
        self.assertTrue( p2.id == p2a.id )

        session.flush(p1)
        session.flush(p2)

    #@unittest.skip("because")
    def testGameWithPlayer(self):
        parser = LogFileParser(self.session)
        parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()

        g = Game(self.session, parser.get_players())

        p1 = g.game_players[0]
        p2 = g.game_players[1]
        g.game_winner = p1


        session = self.session
        session.add(g)
        session.commit()


        my_g = self.persistence_manager.get_game(g.id)
        self.assertTrue( my_g is not None)
        self.assertEqual( g.game_name, my_g.game_name)
        self.assertTrue( len(g.game_players) == 2 )
        self.assertEqual( g.game_players[0].name , "Ryan")
        self.assertTrue( g.game_players[1].name == "sozin")
        self.assertTrue( g.game_winner is not None)
        self.assertTrue( g.game_winner.name == "Ryan")


        my_player1 = self.persistence_manager.get_player(p1)
        self.assertEqual("Ryan", my_player1.name)
        self.assertTrue( my_player1.id == g.game_players[0].id)

        my_player2 = self.persistence_manager.get_player(p2)
        self.assertEqual("sozin", my_player2.name)
        self.assertTrue( my_player2.id == g.game_players[1].id )

        #change the name of something and verify that the id remains the game
        p1.name = "Darth Vader"
        session.add(p1)
        session.commit()

        vader = self.persistence_manager.get_player(p1)
        self.assertEqual( my_player1.id, vader.id )

    #@unittest.skip("because")
    def testTape(self):

        session = self.session

        parser = LogFileParser(self.session)
        parser.read_input_from_file("../logfiles/fsm_test_input.txt")
        parser.run_finite_state_machine()
        game_tape = parser.game_tape

        g = Game(self.session, parser.get_players())

        p1 = g.game_players[0]
        p2 = g.game_players[1]


        for throw_result in game_tape:
            g.game_throws.append(throw_result)

        session.add(g)
        session.commit()


        #now get 'em back
        my_g = self.persistence_manager.get_game(g.id)
        self.assertTrue( g is not None )

        throws = my_g.game_throws
        self.assertTrue( throws is not None)
        self.assertEqual( len(throws) , 8 )

        #* *** Ryan Rolls to Attack: [Focus], [Blank], [], [], [], [], [] ***
        #* *** Ryan turns Attack Die 1 (Focus) into a [Hit] ***
        throw = throws[0]
        self.assertEqual( g.id, throw.game_id)
        self.assertEqual( p1.name, throw.player.name)
        self.assertEqual( DiceThrowType.ATTACK, throw.throw_type )
        self.assertEqual( 1, throw.attack_set_num)

        result = throw.results[0]
        self.assertEqual( 1, result.dice_num)
        self.assertEqual( DiceType.RED, result.dice.dice_type)
        self.assertEqual( DiceFace.FOCUS, result.dice.dice_face)
        self.assertEqual( 1, len (result.adjustments))
        self.assertEqual( DiceFace.HIT, result.final_dice.dice_face)

        adjustment = result.adjustments[0]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.CONVERT, adjustment.adjustment_type)
        self.assertEqual( DiceFace.FOCUS, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.HIT, adjustment.to_dice.dice_face)

        result = throw.results[1]
        self.assertEqual( 2, result.dice_num)
        self.assertEqual( DiceType.RED, result.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, result.dice.dice_face)
        self.assertEqual( 0, len (result.adjustments))
        self.assertEqual( DiceFace.BLANK, result.final_dice.dice_face)


        #* *** sozin Rolls to Defend: [Evade], [Blank], [Evade], [], [], [], [] ***
        throw = throws[1]
        self.assertEqual( g.id, throw.game_id)
        self.assertEqual( p2.name, throw.player.name)
        self.assertEqual( DiceThrowType.DEFEND, throw.throw_type )
        self.assertEqual( 1, throw.attack_set_num)

        result = throw.results[0]
        self.assertEqual( 1, result.dice_num)
        self.assertEqual( DiceType.GREEN, result.dice.dice_type)
        self.assertEqual( DiceFace.EVADE, result.dice.dice_face)
        self.assertEqual( 0, len (result.adjustments))
        self.assertEqual( DiceFace.EVADE, result.final_dice.dice_face)

        result = throw.results[1]
        self.assertEqual( 2, result.dice_num)
        self.assertEqual( DiceType.GREEN, result.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, result.dice.dice_face)
        self.assertEqual( 0, len (result.adjustments))
        self.assertEqual( DiceFace.BLANK, result.final_dice.dice_face)

        result = throw.results[2]
        self.assertEqual( 3, result.dice_num)
        self.assertEqual( DiceType.GREEN, result.dice.dice_type)
        self.assertEqual( DiceFace.EVADE, result.dice.dice_face)
        self.assertEqual( 0, len (result.adjustments))
        self.assertEqual( DiceFace.EVADE, result.final_dice.dice_face)


        #* *** Ryan Rolls to Attack: [Hit], [Crit], [], [], [], [], [] ***
        throw = throws[2]
        self.assertEqual( g.id, throw.game_id)
        self.assertEqual( p1.name, throw.player.name)
        self.assertEqual( DiceThrowType.ATTACK, throw.throw_type )
        self.assertEqual( 2, throw.attack_set_num)
        self.assertEqual( 2, len( throw.results ))


        result = throw.results[0]
        self.assertEqual( 1, result.dice_num)
        self.assertEqual( DiceType.RED, result.dice.dice_type)
        self.assertEqual( DiceFace.HIT, result.dice.dice_face)
        self.assertEqual( DiceFace.HIT, result.final_dice.dice_face)
        self.assertEqual( 0, len (result.adjustments))

        result = throw.results[1]
        self.assertEqual( 2, result.dice_num)
        self.assertEqual( DiceType.RED, result.dice.dice_type)
        self.assertEqual( DiceFace.CRIT, result.dice.dice_face)
        self.assertEqual( DiceFace.CRIT, result.final_dice.dice_face)
        self.assertEqual( 0, len (result.adjustments))

        #* *** sozin Rolls to Defend: [Focus], [], [], [], [], [], [] ***
        #* *** sozin turns Defense Die 1 (Focus) into a [Evade] ***
        throw = throws[3]
        self.assertEqual( g.id, throw.game_id)
        self.assertEqual( p2.name, throw.player.name)
        self.assertEqual( DiceThrowType.DEFEND, throw.throw_type )
        self.assertEqual( 2, throw.attack_set_num)
        self.assertEqual( 1, len( throw.results))

        result = throw.results[0]
        self.assertEqual( 1, result.dice_num)
        self.assertEqual( DiceType.GREEN, result.dice.dice_type)
        self.assertEqual( DiceFace.FOCUS, result.dice.dice_face)
        self.assertEqual( DiceFace.EVADE, result.final_dice.dice_face)
        self.assertEqual( 1, len (result.adjustments))

        adjustment = result.adjustments[0]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.CONVERT, adjustment.adjustment_type)
        self.assertEqual( DiceFace.FOCUS, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.EVADE, adjustment.to_dice.dice_face)

        #* *** sozin Rolls to Attack: [Blank], [Blank], [], [], [], [], [] ***
        #<sozin> - tl
        #* *** sozin Re-Rolls Attack Die 1 [Blank] and gets a [Focus] ***
        #* *** sozin Re-Rolls Attack Die 2 [Focus] and gets a [Focus] ***
        #* *** sozin turns Attack Die 1 (Focus) into a [Hit] ***
        #* *** sozin turns Attack Die 2 (Focus) into a [Hit] ***
        throw = throws[4]
        self.assertEqual( g.id, throw.game_id)
        self.assertEqual( p2.name, throw.player.name)
        self.assertEqual( DiceThrowType.ATTACK, throw.throw_type )
        self.assertEqual( 3, throw.attack_set_num)
        self.assertEqual( 2, len( throw.results))

        result = throw.results[0]
        self.assertEqual( 1, result.dice_num)
        self.assertEqual( DiceType.RED, result.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, result.dice.dice_face)
        self.assertEqual( DiceFace.HIT, result.final_dice.dice_face)
        self.assertEqual( 1, len (result.adjustments))

        adjustment = result.adjustments[0]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.REROLL, adjustment.adjustment_type)
        self.assertEqual( DiceFace.BLANK, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.HIT, adjustment.to_dice.dice_face)


        result = throw.results[1]
        self.assertEqual( 2, result.dice_num)
        self.assertEqual( DiceType.RED, result.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, result.dice.dice_face)
        self.assertEqual( DiceFace.CRIT, result.final_dice.dice_face)
        self.assertEqual( 2, len (result.adjustments))

        adjustment = result.adjustments[0]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.REROLL, adjustment.adjustment_type)
        self.assertEqual( DiceFace.BLANK, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.FOCUS, adjustment.to_dice.dice_face)

        adjustment = result.adjustments[1]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.CONVERT, adjustment.adjustment_type)
        self.assertEqual( DiceFace.FOCUS, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.CRIT, adjustment.to_dice.dice_face)

        #* *** Ryan Rolls to Defend: [Focus], [Blank], [Focus], [], [], [], [] ***
        #* *** Ryan Re-Rolls Defense Die 2 (Blank) and gets a [Focus] ***
        #* *** Ryan turns Defense Die 1 (Focus) into a [Evade] ***
        #* *** Ryan turns Defense Die 2 (Focus) into a [Evade] ***
        #* *** Ryan turns Defense Die 3 (Focus) into a [Evade] ***

        throw = throws[5]
        self.assertEqual( g.id, throw.game_id)
        self.assertEqual( p1.name, throw.player.name)
        self.assertEqual( DiceThrowType.DEFEND, throw.throw_type )
        self.assertEqual( 3, throw.attack_set_num)
        self.assertEqual( 3, len( throw.results))

        result = throw.results[0]
        self.assertEqual( 1, result.dice_num)
        self.assertEqual( DiceType.GREEN, result.dice.dice_type)
        self.assertEqual( DiceFace.FOCUS, result.dice.dice_face)
        self.assertEqual( DiceFace.EVADE, result.final_dice.dice_face)
        self.assertEqual( 1, len (result.adjustments))

        adjustment = result.adjustments[0]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.CONVERT, adjustment.adjustment_type)
        self.assertEqual( DiceFace.FOCUS, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.EVADE, adjustment.to_dice.dice_face)

        result = throw.results[1]
        self.assertEqual( 2, result.dice_num)
        self.assertEqual( DiceType.GREEN, result.dice.dice_type)
        self.assertEqual( DiceFace.BLANK, result.dice.dice_face)
        self.assertEqual( DiceFace.EVADE, result.final_dice.dice_face)
        self.assertEqual( 2, len (result.adjustments))

        adjustment = result.adjustments[0]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.REROLL, adjustment.adjustment_type)
        self.assertEqual( DiceFace.BLANK, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.FOCUS, adjustment.to_dice.dice_face)


        adjustment = result.adjustments[1]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.CONVERT, adjustment.adjustment_type)
        self.assertEqual( DiceFace.FOCUS, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.EVADE, adjustment.to_dice.dice_face)

        result = throw.results[2]
        self.assertEqual( 3, result.dice_num)
        self.assertEqual( DiceType.GREEN, result.dice.dice_type)
        self.assertEqual( DiceFace.FOCUS, result.dice.dice_face)
        self.assertEqual( DiceFace.EVADE, result.final_dice.dice_face)
        self.assertEqual( 1, len (result.adjustments))

        adjustment = result.adjustments[0]
        self.assertEqual( adjustment.base_result_id, result.id)
        self.assertEqual( DiceThrowAdjustmentType.CONVERT, adjustment.adjustment_type)
        self.assertEqual( DiceFace.FOCUS, adjustment.from_dice.dice_face )
        self.assertEqual( DiceFace.EVADE, adjustment.to_dice.dice_face)



if __name__ == "__main__":
    if len (sys.argv) == 1:
        unittest.main()
    elif sys.argv[1] == 'create':
        pm = PersistenceManager(db_connector)
        pm.create_schema()
        pm.populate_reference_tables()
        db_connector.get_session().commit()
        db_connector.get_session().close_all()
    elif sys.argv[1] == 'destroy':
        pm = PersistenceManager(db_connector)
        pm.drop_schema()
        db_connector.get_session().commit()
        db_connector.get_session().close_all()