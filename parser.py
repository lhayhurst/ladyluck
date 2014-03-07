
from __future__ import print_function
import re
from fsm import fsm
from model import DiceRoll, AttackSet


class LogFileParser:

    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.lines = []
        self.turns = []
        self.current_turn = None

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
        return self.turns

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

    def get_dice_rolled(self, line):
        dice_rolled = re.findall(r'\[(.*?)\]', line)
        dice_rolled[:] = (value for value in dice_rolled if len(value) > 0)
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


    def begin_attack_set(self, fsm, value ):
        attacking_player = None
        defending_player = None
        #pull out the player from the line
        if self.is_player_one(value):
            attacking_player = self.player1
            defending_player = self.player2
        elif self.is_player_two(value):
            attacking_player = self.player2
            defending_player  = self.player1
        else:
            RuntimeError("Third player detected, bombing out!")

        self.current_turn = AttackSet(attacking_player, defending_player)

        dice_rolled = self.get_dice_rolled( value )

        i = 1
        for d in dice_rolled:
            dr = DiceRoll( d, i, attacking_player )
            self.current_turn.add_attack_roll( dr )
            i += 1

    def end_attack_set(self, fss, value):
        self.turns.append(self.current_turn)

    def end_attack_set_and_begin_new_attack_set(self, fss, value):
        self.turns.append(self.current_turn)
        self.begin_attack_set(fss, value)

    def add_defense(self, fss, value):
        dice_rolled = self.get_dice_rolled(value)
        defending_player = self.player_rolling_dice(value)

        i = 1
        for d in dice_rolled:
            dr = DiceRoll( d, i, defending_player)
            self.current_turn.add_defense_roll( dr )
            i += 1

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


    def add_attack_modification(self,fss,value):
        dice = []
        if self.player_rerolled_attack_dice(value):
            dice = self.get_attack_dice_rerolled(value)
        elif self.player_turned_attack_dice(value):
            dice = self.get_attack_dice_changed_by_set(value)

        dice_num = dice[0][0]
        dice_val = dice[0][1]
        rs = self.current_turn
        rs.add_attack_reroll(dice_num, dice_val)

    def get_defense_dice_rerolled(self, line):
        dice_rolled = re.findall(r'.*?Re-Rolls\s+Defense\s+Dice\s+(\d+).*?and\s+gets\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    def get_defense_dice_changed_by_set(self, line):
        dice_rolled = re.findall(r'.*?turns\s+Defense\s+Die\s+(\d+).*?into\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    def add_defense_modification(self,fss,value):
        dice = []
        if self.player_rerolled_defense_dice(value):
            dice = self.get_defense_dice_rerolled(value)
        elif self.player_turned_defense_dice(value):
            dice = self.get_defense_dice_changed_by_set(value)
        dice_num = dice[0][0]
        dice_val = dice[0][1]
        rs = self.current_turn
        rs.add_defense_reroll(dice_num, dice_val)
