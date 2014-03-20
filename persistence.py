import os
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
game_roll_table            = "game_roll"
game_players_table         = "game_players"
game_winner_table          = "game_winner"
game_roll_table            = 'game_roll_type'
player_table               = "player"
dice_table                 = 'dice'
game_table                 = "game"

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

class DiceThrowAdjustment(DeclEnum):
    REROLL  = 'R', 'REROLL'
    CONVERT = 'C', 'CONVERT'

class GameRollType(DeclEnum):
    ATTACK_DICE = "A", "ATTACK"
    ATTACK_DICE_REROLL = "B", "ATTACK REROLL"
    ATTACK_DICE_MODIFICATION = "C", "ATTACK MODIFICATION"
    DEFENSE_DICE = "D", "DEFENSE"
    DEFENSE_DICE_REROLL = "E", "DEFENSE REROLL"
    DEFENSE_DICE_MODIFICATION = "F", "DEFENSE MODIFICATION"

class Player(Base):
    __tablename__ = player_table
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable = False, index=True)

    def __repr__(self):
        return "<Player(id={0}name={1}".format(self.id, self.name)

    def __init__(self, name):
        self.name = name


class Dice(Base):
    __tablename__ = dice_table
    id        = Column(Integer, primary_key=True)
    dice_type = Column(DiceType.db_type())
    dice_face = Column(DiceFace.db_type())

class GameRoll(Base):

    __tablename__ = game_roll_table
    id             = Column(Integer, primary_key=True)
    game_id        = Column(Integer,ForeignKey('{0}.id'.format(game_table)) )
    player_id      = Column(Integer, ForeignKey('{0}.id'.format(player_table)))
    roll_type      = Column(GameRollType.db_type())
    dice_id        = Column(Integer, ForeignKey('{0}.id'.format(dice_table)))
    attack_set_num = Column(Integer)
    dice_num       = Column(Integer)
    player         = relationship( Player.__name__)
    dice           = relationship( Dice.__name__)

class Game(Base):
    __tablename__ = game_table
    id               = Column(Integer, primary_key=True)
    game_played_time = Column(DateTime)
    game_name        = Column(String(128))
    game_players     = relationship( Player.__name__, secondary=GamePlayers  )
    game_roll        = relationship( GameRoll.__name__, order_by="asc(GameRoll.id)")
    game_winner      = relationship( Player.__name__, secondary=GameWinner, uselist=False )

    def __init__(self, player1, player2, winner=None):
        self.game_played_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.game_players.append( player1 )
        self.game_players.append( player2 )
        self.game_name = "{0} v {1} ({2}".format(player1.name, player2.name, self.game_played_time )
        if winner is not None:
            self.game_winner = winner

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





