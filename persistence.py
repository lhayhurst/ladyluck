from sqlalchemy.orm import sessionmaker, relationship
import time
from decl_enum import DeclEnum

__author__ = 'lhayhurst'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Table, Enum
from sqlalchemy import ForeignKey

Base = declarative_base()
Session = sessionmaker()

player_table = "player"
game_table   = "game"
game_players_table = "game_players"
game_tape_entry_table = "game_tape_entry"

GamePlayers = Table( game_players_table, Base.metadata,
    Column('game_id', Integer, ForeignKey('{0}.id'.format(game_table))),
    Column('player_id', Integer, ForeignKey('{0}.id'.format(player_table)))
)

class DiceType(DeclEnum):
    RED   = 'R', "Red Attack Dice"
    GREEN = 'G', "Green Attack Dice"

class DiceFace(DeclEnum):
    HIT   = 'H', "Hit"
    CRIT  = "C", "Crit"
    FOCUS = "F", "Focus"
    BLANK = "B", "Blank"
    EVADE = "E", "Evade"

game_tape_entry_type_table = 'game_tape_entry_type'
class GameTapeEntryType(DeclEnum):
    ATTACK_DICE = "A", "Attack Dice"
    ATTACK_DICE_REROLL = "B", "Attack Dice Reroll"
    ATTACK_DICE_MODIFICATION = "C", "Attack Dice Modification"
    DEFENSE_DICE = "D", "Defense Dice"
    DEFENSE_DICE_REROLL = "E", "Defense Dice Reroll"
    DEFENSE_DICE_MODIFICATION = "F", "Defense Dice Modification"

class Player(Base):
    __tablename__ = player_table
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable = False, index=True)

    def __repr__(self):
        return "<Player(id={0}name={1}".format(self.id, self.name)

    def __init__(self, name):
        self.name = name



dice_table = 'dice'
class Dice(Base):
    __tablename__ = dice_table
    id        = Column(Integer, primary_key=True)
    dice_type = Column(DiceType.db_type())
    dice_face = Column(DiceFace.db_type())

class GameTapeEntry(Base):

    __tablename__ = game_tape_entry_table
    id             = Column(Integer, primary_key=True)
    game_id        = Column(Integer,ForeignKey('{0}.id'.format(game_table)) )
    player_id      = Column(Integer, ForeignKey('{0}.id'.format(player_table)))
    tape_type      = Column(GameTapeEntryType.db_type())
    dice_id        = Column(Integer, ForeignKey('{0}.id'.format(dice_table)))
    attack_set_num = Column(Integer)
    dice_num       = Column(Integer)
    player         = relationship( Player.__name__)
    dice           = relationship( Dice.__name__)

class Game(Base):
    __tablename__ = game_table
    id = Column(Integer, primary_key=True)
    game_played_time = Column(DateTime)
    game_name = Column(String(128))
    game_players = relationship( Player.__name__, secondary=GamePlayers  ) #TODO: why 'Player' and not playertable?
    game_tape    = relationship( GameTapeEntry.__name__, order_by="asc(GameTapeEntry.id)")

    def __init__(self, player1, player2):
        self.game_played_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.game_players.append( player1 )
        self.game_players.append( player2 )
        self.game_name = "{0} v {1} ({2}".format(player1.name, player2.name, self.game_played_time )





