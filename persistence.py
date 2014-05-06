import os
from flask import url_for
import sqlalchemy

__author__ = 'lhayhurst'

import time
from decl_enum import DeclEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Table
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker, relationship

#static database objects
Base = declarative_base()
Session = sessionmaker()

#TABLES
game_roll_table             = "game_roll"
game_players_table          = "game_players"
game_winner_table           = "game_winner"
game_roll_table             = 'game_roll_type'
player_table                = "player"
dice_table                  = 'dice'
game_table                  = "game"
dice_throw_table            = "dice_throw"
dice_throw_result_table     = "dice_throw_result"
dice_throw_adjustment_table = "dice_throw_adjustment"

GamePlayers = Table( game_players_table, Base.metadata,
    Column('game_id', Integer, ForeignKey('{0}.id'.format(game_table))),
    Column('player_id', Integer, ForeignKey('{0}.id'.format(player_table)))
)

GameWinner = Table(game_winner_table, Base.metadata,
    Column('game_id', Integer, ForeignKey('{0}.id'.format(game_table))),
    Column('player_id', Integer, ForeignKey('{0}.id'.format(player_table)))
)

class DiceType(DeclEnum):
    RED   = 'R', "RED"
    GREEN = 'G', "GREEN"

class DiceFace(DeclEnum):
    HIT   = 'H', "HIT"
    CRIT  = "C", "CRIT"
    FOCUS = "F", "FOCUS"
    BLANK = "B", "BLANK"
    EVADE = "E", "EVADE"

class DiceThrowType(DeclEnum):
    ATTACK = 'A', 'ATTACK'
    DEFEND = 'D', 'DEFEND'

class DiceThrowAdjustmentType(DeclEnum):
    REROLL  = 'R', 'REROLL'
    CONVERT = 'C', 'CONVERT'
    NONE    = 'N', 'NONE'

class Player(Base):
    __tablename__ = player_table
    id            = Column(Integer, primary_key=True)
    name          = Column(String(64), nullable = False, index=True)

    def __repr__(self):
        return "<Player(id={0}name={1}".format(self.id, self.name)

    def __init__(self, name):
        self.name = name


class Dice(Base):
    __tablename__ = dice_table
    id        = Column(Integer, primary_key=True)
    dice_type = Column(DiceType.db_type())
    dice_face = Column(DiceFace.db_type())

    def is_hit(self):
        return self.dice_face == DiceFace.HIT

    def is_crit(self):
        return self.dice_face == DiceFace.CRIT

    def is_focus(self):
        return self.dice_face == DiceFace.FOCUS

    def is_blank(self):
        return self.dice_face == DiceFace.BLANK

    def is_evade(self):
        return self.dice_face == DiceFace.EVADE

    def is_attack(self):
        return self.dice_type == DiceType.RED

    def is_defense(self):
        return self.dice_type == DiceType.GREEN



class DiceThrowAdjustment(Base):
    __tablename__      = dice_throw_adjustment_table
    id                 = Column(Integer, primary_key=True)
    base_result_id     = Column(Integer, ForeignKey('{0}.id'.format(dice_throw_result_table)))
    from_dice_id       = Column(Integer, ForeignKey('{0}.id'.format(dice_table)))
    to_dice_id         = Column(Integer, ForeignKey('{0}.id'.format(dice_table)))
    adjustment_type    = Column(DiceThrowAdjustmentType.db_type())
    from_dice          = relationship(Dice.__name__, foreign_keys='DiceThrowAdjustment.from_dice_id')
    to_dice          = relationship(Dice.__name__, foreign_keys='DiceThrowAdjustment.to_dice_id')

class DiceThrowResult(Base):
    __tablename__        = dice_throw_result_table
    id                   = Column(Integer, primary_key=True)
    dice_throw_id        = Column(Integer, ForeignKey('{0}.id'.format(dice_throw_table))) #parent
    dice_num             = Column(Integer)
    dice_result_id       = Column(Integer, ForeignKey('{0}.id'.format(dice_table)))
    final_dice_result_id = Column(Integer, ForeignKey('{0}.id'.format(dice_table)))
    dice                 = relationship( Dice.__name__, foreign_keys='DiceThrowResult.dice_result_id', uselist=False)
    final_dice           = relationship( Dice.__name__, foreign_keys='DiceThrowResult.final_dice_result_id', uselist=False )
    adjustments          = relationship( DiceThrowAdjustment.__name__ )

class DiceThrow(Base):
    __tablename__  = dice_throw_table
    id             = Column(Integer, primary_key=True)
    game_id        = Column(Integer,ForeignKey('{0}.id'.format(game_table)) )
    player_id      = Column(Integer, ForeignKey('{0}.id'.format(player_table)))
    throw_type     = Column(DiceThrowType.db_type())
    attack_set_num = Column(Integer)
    player         = relationship( Player.__name__, uselist=False)
    results        = relationship(DiceThrowResult.__name__)

class Game(Base):
    __tablename__ = game_table
    id               = Column(Integer, primary_key=True)
    game_played_time = Column(DateTime)
    game_name        = Column(String(128))
    game_players     = relationship( Player.__name__, secondary=GamePlayers  )
    game_throws      = relationship( DiceThrow.__name__)
    game_winner      = relationship( Player.__name__, secondary=GameWinner, uselist=False )


    def __init__(self, players, winner=None):
        self.game_played_time = time.strftime('%Y-%m-%d %H:%M:%S')
        for player in players:
            self.game_players.append(  Player( player ))
        self.game_name = "{0} v {1} ({2}".format(self.game_players[0].name, self.game_players[1].name, self.game_played_time )
        if winner is not None:
            self.game_winner = winner

    def id_str(self):
        return str(self.id)

    def sparkline(self, player):
        return url_for("sparkline", game_id=self.id_str(), player=player )

    #these methods are utility methods to help out the game_summary web page.
    def total_reds(self, player):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.total_reds( player )

    def total_greens(self, player):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.total_greens( player )

    def unmodified_hits(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.unmodified_hits( player )

    def expected_unmodified_evades(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.expected_unmodified_evades( player )

    def unmodified_evades(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.unmodified_evades( player )

    def expected_unmodified_hits(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.expected_unmodified_hits( player )

    def unmodified_crits(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.unmodified_crits( player )

    def expected_unmodified_crits(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.expected_unmodified_crits( player )

    def unmodified_focuses(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.unmodified_focuses( player )

    def expected_unmodified_focuses(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.expected_unmodified_focuses( player )

    def unmodified_green_focuses(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.unmodified_green_focuses( player )

    def expected_unmodified_green_focuses(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.expected_unmodified_green_focuses( player )

    def unmodified_blanks(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.unmodified_blanks( player )

    def expected_unmodified_blanks(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.expected_unmodified_blanks( player )

    def unmodified_green_blanks(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.unmodified_green_blanks( player )

    def expected_unmodified_green_blanks(self, player ):
        if self.game_tape == None:
            return 0
        else:
            return self.game_tape.expected_unmodified_green_blanks( player )

class PersistenceManager:
    def __init__(self, echo=False):
        url = os.getenv('DB_TEST_URL')
        self.engine = sqlalchemy.create_engine(url, echo=echo)
        self.connection = self.engine.connect()

        Session.configure(bind=self.engine)
        self.session = Session()

    def create_schema(self):
        Base.metadata.create_all(self.engine)

    def drop_schema(self):
        Base.metadata.drop_all(self.engine)


    def populate_reference_tables(self):
        #return True
        self.session.add_all( [
            Dice( dice_type=DiceType.RED, dice_face=DiceFace.HIT ),
            Dice( dice_type=DiceType.RED, dice_face=DiceFace.CRIT ),
            Dice( dice_type=DiceType.RED, dice_face=DiceFace.FOCUS ),
            Dice( dice_type=DiceType.RED, dice_face=DiceFace.BLANK ),
            Dice( dice_type=DiceType.GREEN, dice_face=DiceFace.EVADE ),
            Dice( dice_type=DiceType.GREEN, dice_face=DiceFace.FOCUS),
            Dice( dice_type=DiceType.GREEN, dice_face=DiceFace.BLANK ) ] )

    def get_games(self):
        return self.session.query(Game).all()

    def get_game(self, game_id):
        return self.session.query(Game).filter_by(id=game_id).first()

    def get_dice(self, dice_type, dice_face):
        return self.session.query(Dice).filter_by(dice_type=dice_type, dice_face=dice_face).first()

    def get_player(self, player):
        return self.session.query(Player).filter_by(name=player.name).first()





