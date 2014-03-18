
from __future__ import print_function
import re
from fsm import fsm
from model import GameTape, GameTapeEntry
from persistence import GameTapeEntryType, DiceType, DiceFace


class LogFileParser:

    def __init__(self):
        self.lines = []
        self.game_tape = GameTape()
        self.current_attack_set = 0

    def read_input_from_string(self, input):
        lines = input.split('\n')[:-1]
        self.clean_up_lines( lines  )

    def read_input_from_file(self, file):
        f = open( file or "log.txt", 'r')
        #strip out all the non-dice rolls.
        alllines = f.readlines()
        f.close()

        self.clean_up_lines(alllines)

    def clean_up_lines(self, lines):

        for line in lines:
            if self.player_is_rolling_dice(line) and len(line) > 0:
 #               print(line, end="")
                self.lines.append( line )


    START = "Start"
    PLAYER_ATTACKING = "Player Rolling Attack Dice"
    PLAYER_NOT_ROLLING_DICE = "Player Not Rolling Dice"
    PLAYER_DEFENDING = "Player Defending"
    PLAYER_MODIFYING_DEFENSE_DICE = "Player Modifying Defense Dice"
    PLAYER_MODIFYING_ATTACK_DICE = "Player Modifying Attack Dice"


    def run_finite_state_machine(self ):


        fs = fsm( [
            (
                LogFileParser.START,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.begin_attack_set
            ),
            (
                LogFileParser.PLAYER_ATTACKING,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            (
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            (
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            (
                LogFileParser.START,
                LogFileParser.PLAYER_DEFENDING,
                lambda x: self.player_is_defending(x)
            ),
            (
                LogFileParser.PLAYER_ATTACKING,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.end_attack_set_and_begin_new_attack_set
            ),
            (
                LogFileParser.PLAYER_ATTACKING,
                LogFileParser.PLAYER_DEFENDING,
                lambda x: self.player_is_defending(x),
                self.add_defense
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.end_attack_set_and_begin_new_attack_set
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                lambda x: self.player_is_modifying_attack_dice(x)
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                lambda x: self.player_is_modifying_defense_dice(x),
                self.add_defense_modification
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_DEFENDING,
                lambda x: self.player_is_defending(x),
                self.add_defense
            ),
            (
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                lambda x: self.player_is_modifying_defense_dice(x),
                self.add_defense_modification
            ),
            (
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.end_attack_set_and_begin_new_attack_set
            ),
            (
                LogFileParser.PLAYER_ATTACKING,
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                lambda x: self.player_is_modifying_attack_dice(x),
                self.add_attack_modification
            ),
            (
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                lambda x: self.player_is_modifying_attack_dice(x),
                self.add_attack_modification
            ),
            (
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.end_attack_set_and_begin_new_attack_set
            ),
            (
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                LogFileParser.PLAYER_DEFENDING,
                lambda x: self.player_is_defending(x),
                self.add_defense
            )

        ] )

        fs.start(LogFileParser.START)

        for line in self.get_lines():
            fs.event(line)

        fs.event("")


    def get_roll_sets(self):
        return self.attack_sets

    def is_player_one(self,line):
        player = self.player_rolling_dice(line)
        if self.player1 == None and self.player2 == None:
            self.player1 = player
            return True
        elif self.player1 == player:
            return True
        elif self.player1 != None and self.player2 == None:
            self.player2 = player
            return False
        elif self.player2 == player:
            return False
        else:
            RuntimeError("Third player {0} found??!!".format(player))

    def is_player_two(self, line):
        return not self.is_player_one(line)

    def get_lines(self):
        return self.lines


    face_translate = { "Hit"  : DiceFace.HIT,
                      "Crit"  : DiceFace.CRIT,
                      "Focus" : DiceFace.FOCUS,
                      "Blank" : DiceFace.BLANK,
                      "Evade" : DiceFace.EVADE }


    def get_dice_rolled(self, line):
        dice_rolled = re.findall(r'\[(.*?)\]', line)
        dice_rolled[:] = (LogFileParser.face_translate[value] for value in dice_rolled if len(value) > 0)
        return dice_rolled

    def player_is_rolling_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+[Rolls|Re-rolls|turns].*?\*\*\*',line)

    def player_rolling_dice(self, line):
        match = re.match(r'^\* \*\*\*\s+(.*?)\s+[Rolls|Re-rolls|turns].*?\*\*\*',line)
        if match:
            return match.group(1)
        else:
            return None

    def is_attack_roll(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Rolls\s+to\s+Attack.*?\*\*\*',line)

    def is_defense_roll(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Rolls\s+to\s+Defend.*?\*\*\*',line)

    def player_is_defending(self, line):
        if self.player_is_rolling_dice(line):
            if self.is_defense_roll(line):
                return True
        return False

    def player_is_rolling_attack_dice(self, line ):
        return self.player_is_rolling_dice(line) and self.is_attack_roll(line)


    def begin_attack_set(self, game_state, value ):
        self.current_attack_set += 1
        attacking_player = self.player_rolling_dice(value)

        dice_rolled = self.get_dice_rolled( value )

        dice_number = 1
        for dice_value in dice_rolled:
            self.game_tape.add( GameTapeEntry( attacking_player,
                                               None,
                                               game_state.currentState,
                                               self.current_attack_set,
                                               GameTapeEntryType.ATTACK_DICE,
                                               DiceType.RED,
                                               dice_number,
                                               dice_value)  )
            dice_number += 1

    def end_attack_set(self, fss, value):
        return True


    def end_attack_set_and_begin_new_attack_set(self, game_state, value):
        self.begin_attack_set(game_state, value)

    def add_defense(self, fss, value):
        dice_rolled = self.get_dice_rolled(value)
        defending_player = self.player_rolling_dice(value)

        dice_number = 1
        for dice_value in dice_rolled:
            self.game_tape.add( GameTapeEntry( defending_player,
                                               None,
                                               fss.currentState,
                                               self.current_attack_set,
                                               GameTapeEntryType.DEFENSE_DICE,
                                               DiceType.GREEN,
                                               dice_number,
                                               dice_value) )
            dice_number += 1

    def player_rerolled_defense_dice(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Re-Rolls\s+Defense\s+Die.*?\*\*\*',line)

    def player_turned_defense_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+turns\s+Defense\s+Die.*?\*\*\*',line)

    def player_rerolled_attack_dice(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Re-Rolls\s+Attack\s+Die.*?\*\*\*',line)

    def player_turned_attack_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+turns\s+Attack\s+Die.*?\*\*\*',line)


    def player_is_modifying_defense_dice(self, value):
        return self.player_rerolled_defense_dice(value) or\
               self.player_turned_defense_dice(value)

    def player_is_modifying_attack_dice(self, value):
        return self.player_rerolled_attack_dice(value) or\
               self.player_turned_attack_dice(value)



    #* *** sozin Re-Rolls Attack Die 1 [Focus] and gets a [Hit] ***
    def get_attack_dice_rerolled(self, line):
        dice_rolled = re.findall(r'.*?Re-Rolls\s+Attack\s+Die\s+(\d+).*?and\s+gets\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    #* *** sozin turns Attack Die 1 (Focus) into a [Hit] ***
    def get_attack_dice_changed_by_set(self, line):
        dice_rolled = re.findall(r'.*?turns\s+Attack\s+Die\s+(\d+).*?into\s+a\s+\[(.*?)\]', line)
        return dice_rolled


    def add_attack_modification(self,game_state,value):
        dice = []
        event_type = None
        if self.player_rerolled_attack_dice(value):
            dice = self.get_attack_dice_rerolled(value)
            event_type = GameTapeEntryType.ATTACK_DICE_REROLL
        elif self.player_turned_attack_dice(value):
            dice = self.get_attack_dice_changed_by_set(value)
            event_type = GameTapeEntryType.ATTACK_DICE_MODIFICATION

        dice_number = int(dice[0][0])
        dice_value = LogFileParser.face_translate[dice[0][1]]
        attacking_player = self.player_rolling_dice(value)

        self.game_tape.add( GameTapeEntry( attacking_player,
                                           None,
                                           game_state.currentState,
                                           self.current_attack_set,
                                           event_type,
                                           DiceType.RED,
                                           dice_number,
                                           dice_value)  )

    def get_defense_dice_rerolled(self, line):
        dice_rolled = re.findall(r'.*?Re-Rolls\s+Defense\s+Die\s+(\d+).*?and\s+gets\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    def get_defense_dice_changed_by_set(self, line):
        dice_rolled = re.findall(r'.*?turns\s+Defense\s+Die\s+(\d+).*?into\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    def add_defense_modification(self,game_state,value):
        dice = []
        event_type = None
        if self.player_rerolled_defense_dice(value):
            dice = self.get_defense_dice_rerolled(value)
            event_type = GameTapeEntryType.DEFENSE_DICE_REROLL
        elif self.player_turned_defense_dice(value):
            dice = self.get_defense_dice_changed_by_set(value)
            event_type = GameTapeEntryType.DEFENSE_DICE_MODIFICATION

        dice_number = int(dice[0][0])
        dice_value = LogFileParser.face_translate[dice[0][1]]

        defending_player = self.player_rolling_dice(value)

        self.game_tape.add( GameTapeEntry( defending_player,
                                           None,
                                           game_state.currentState,
                                           self.current_attack_set,
                                           event_type,
                                           DiceType.GREEN,
                                           dice_number,
                                           dice_value ) )


