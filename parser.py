
from __future__ import print_function
from collections import OrderedDict
import re
from fsm import fsm
from persistence import DiceType, DiceFace, DiceThrowType, DiceThrowAdjustmentType, DiceThrow, Player, Dice, \
    DiceThrowResult, DiceThrowAdjustment


class LogFileParser:

    def __init__(self, session):
        self.session = session
        self.lines = []
        self.game_tape = []
        self.players = OrderedDict()
        self.current_attack_set = 0
        self.current_throw = None


    def get_players(self):
        return self.players.keys()

    def add_line(self, line):
        self.clean_up_lines([line])

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
    PLAYER_ADDING_ATTACK_DICE = "Player Adding Attack Dice"
    PLAYER_ADDING_DEFENSE_DICE = "Player Adding Defense Dice"

    def run_finite_state_machine(self ):

        fs = fsm( [
            (
                LogFileParser.START,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.begin_attack_set
            ),
            (
                LogFileParser.START,
                LogFileParser.PLAYER_DEFENDING,
                lambda x: self.player_is_defending(x)
            ),
            (
                LogFileParser.PLAYER_ATTACKING,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
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
                self.add_defense_roll
            ),

            (
                LogFileParser.PLAYER_ATTACKING,
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                lambda x: self.player_is_modifying_attack_dice(x),
                self.add_attack_modification
            ),
            (
                LogFileParser.PLAYER_ATTACKING,
                LogFileParser.PLAYER_ADDING_ATTACK_DICE,
                lambda x: self.player_added_attack_dice(x),
                self.add_attack_dice
            ),
            (
                LogFileParser.PLAYER_ADDING_ATTACK_DICE,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            (
                LogFileParser.PLAYER_ADDING_ATTACK_DICE,
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                lambda x: self.player_is_modifying_attack_dice(x),
                self.add_attack_modification
            ),
            (
                LogFileParser.PLAYER_ADDING_ATTACK_DICE,
                LogFileParser.PLAYER_ADDING_ATTACK_DICE,
                lambda x: self.player_added_attack_dice(x),
                self.add_attack_dice
            ),
            (
                LogFileParser.PLAYER_ADDING_ATTACK_DICE,
                LogFileParser.PLAYER_DEFENDING,
                lambda x: self.player_is_defending(x),
                self.add_defense_roll
            ),
            (
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            (
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                lambda x: self.player_is_modifying_attack_dice(x),
                self.add_attack_modification
            ),
            (
                LogFileParser.PLAYER_MODIFYING_ATTACK_DICE,
                LogFileParser.PLAYER_ADDING_ATTACK_DICE,
                lambda x: self.player_added_attack_dice(x),
                self.add_attack_dice
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
                self.add_defense_roll
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.end_attack_set_and_begin_new_attack_set
            ),
            (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_DEFENDING,
                lambda x: self.player_is_defending(x),
                self.add_defense_roll
            ),
             (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                lambda x: self.player_is_modifying_defense_dice(x),
                self.add_defense_modification
            ),
             (
                LogFileParser.PLAYER_DEFENDING,
                LogFileParser.PLAYER_ADDING_DEFENSE_DICE,
                lambda x: self.player_added_defense_dice(x),
                self.add_defense_dice
            ),
            (
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
            ( LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
              LogFileParser.PLAYER_ADDING_DEFENSE_DICE,
              lambda x: self.player_added_defense_dice(x),
              self.add_defense_dice
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
                LogFileParser.PLAYER_ADDING_DEFENSE_DICE,
                LogFileParser.PLAYER_ADDING_DEFENSE_DICE,
                lambda x: self.player_added_defense_dice(x),
                self.add_defense_dice
            ),
            (
                LogFileParser.PLAYER_ADDING_DEFENSE_DICE,
                LogFileParser.PLAYER_MODIFYING_DEFENSE_DICE,
                lambda x: self.player_is_modifying_defense_dice(x),
                self.add_defense_modification
            ),
            (
                LogFileParser.PLAYER_ADDING_DEFENSE_DICE,
                LogFileParser.PLAYER_ATTACKING,
                lambda x: self.player_is_rolling_attack_dice(x),
                self.end_attack_set_and_begin_new_attack_set
            ),
            (
                LogFileParser.PLAYER_ADDING_DEFENSE_DICE,
                LogFileParser.START,
                lambda x: not self.player_is_rolling_dice(x),
                self.end_attack_set
            ),
        ] )

        fs.start(LogFileParser.START)

        i = 0
        lines = self.get_lines()
        for line in lines:
            try:
                fs.event(line)
            except ValueError:
                print("Unable to transition from state {0} ({1}) using input {2}, ignoring and continuing on ...".format(fs.currentState, lines[i-1], lines[i]))

            i = i + 1 #just for debugging purposes

        fs.event("")


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



    def get_dice_cancelled(self, line):
        dice_added = re.findall( r'cancels\s+.*?(\w+)\s+\*\*\*', line)
        dice_added[:] = (LogFileParser.face_translate[value] for value in dice_added if len(value) > 0)
        return dice_added[0]

    def get_dice_added(self, line):
        dice_added = re.findall( r'added\s+a[n]*\s+(\w+)', line)
        dice_added[:] = (LogFileParser.face_translate[value] for value in dice_added if len(value) > 0)
        return dice_added[0]

    def get_dice_rolled(self, line):
        #some players have the habit of putting []'s in their names, for example 'sepyx [FR]
        #these have to be stripped out before providing them to the below
        pre, post = line.split(':')
        dice_rolled = re.findall(r'\[(.*?)\]', post)
        dice_rolled[:] = (LogFileParser.face_translate[value] for value in dice_rolled if len(value) > 0)
        return dice_rolled

    def player_cancelled_attack_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+cancels\s+.*?[Hit|Crit|Focus|Blank].*?\*\*\*',line)

    def player_cancelled_defense_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+cancels\s+.*?[Evade|Focus|Blank].*?\*\*\*',line)

    def player_added_attack_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+added\s+a\s+[Hit|Crit|Focus|Blank].*?\*\*\*',line)

    def player_added_defense_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+added\s+a[n]*\s+[Evade|Focus|Blank].*?\*\*\*',line)


    def player_is_rolling_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+[Rolls|Re-rolls|turns|added|cancels].*?\*\*\*',line)

    def player_rolling_dice(self, line):
        match = re.match(r'^\* \*\*\*\s+(.*?)\s+[Rolls|Re-rolls|turns].*?\*\*\*',line)
        if match:
            player = match.group(1)
            player = re.sub('[\[\]]', '', player) #strip out pesky brackets
            self.players[player] = 1
            return player
        else:
            return None

    def is_attack_roll(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Rolls\s+to\s+Attack.*?\*\*\*',line)

    def is_defense_roll(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Rolls\s+to\s+Defend.*?\*\*\*',line)

    #* *** Veldrin used Focus on Attack Dice ***
    def player_using_focus_token_on_attack(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+used\s+Focus\s+on\s+Attack\s+Dice.*?\*\*\*',line)

    #* *** Veldrin used Focus on Defense Dice ***
    def player_using_focus_token_on_defense(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+used\s+Focus\s+on\s+Defense\s+Dice.*?\*\*\*',line)

    def player_rerolled_defense_dice(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Re-Rolls\s+Defense\s+Die.*?\*\*\*',line)

    def player_turned_defense_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+turns\s+Defense\s+Die.*?\*\*\*',line)

    def player_rerolled_attack_dice(self,line):
        return re.search(r'^\* \*\*\*\s+.*?\s+Re-Rolls\s+Attack\s+Die.*?\*\*\*',line)

    def player_turned_attack_dice(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+turns\s+Attack\s+Die.*?\*\*\*',line)

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
        dice_throw = DiceThrow( throw_type=DiceThrowType.ATTACK,
                                attack_set_num=self.current_attack_set,
                                player=Player.as_unique( self.session, name=attacking_player))
        for dice_value in dice_rolled:

            dice = Dice(dice_type=DiceType.RED,
                        dice_face=dice_value,
                        dice_origination=Dice.ROLLED)
            throw_result = DiceThrowResult(dice_num=dice_number, dice=dice, final_dice=dice)
            dice_throw.results.append(throw_result)
            dice_number += 1

        self.game_tape.append(dice_throw)
        self.current_throw = dice_throw

    def end_attack_set(self, fss, value):
        return True


    def end_attack_set_and_begin_new_attack_set(self, game_state, value):
        self.begin_attack_set(game_state, value)


    def add_defense_roll(self, fss, value):
        dice_rolled = self.get_dice_rolled(value)
        defending_player = self.player_rolling_dice(value)

        dice_number = 1


        dice_throw = DiceThrow( throw_type=DiceThrowType.DEFEND,
                                attack_set_num=self.current_attack_set,
                                player=Player.as_unique(self.session, name=defending_player))
        for dice_value in dice_rolled:
            dice = Dice( dice_type=DiceType.GREEN,
                         dice_face=dice_value,
                         dice_origination=Dice.ROLLED)
            throw_result = DiceThrowResult(dice_num=dice_number,
                                           dice=dice,
                                           final_dice=dice)
            dice_throw.results.append(throw_result)
            dice_number += 1
        self.game_tape.append(dice_throw)
        self.current_throw = dice_throw

    def player_is_modifying_defense_dice(self, value):
        return self.player_rerolled_defense_dice(value) or\
               self.player_turned_defense_dice(value) or \
               self.player_using_focus_token_on_defense(value) or \
               self.player_cancelled_defense_dice(value)

    def player_is_modifying_attack_dice(self, value):
        return self.player_rerolled_attack_dice(value) or\
               self.player_turned_attack_dice(value) or\
               self.player_using_focus_token_on_attack(value) or\
               self.player_cancelled_attack_dice(value)

    def p(self, line):
        return re.search(r'^\* \*\*\*\s+.*?\s+turns\s+Attack\s+Die.*?\*\*\*',line)

    #* *** sozin Re-Rolls Attack Die 1 [Focus] and gets a [Hit] ***
    def get_attack_dice_rerolled(self, line):
        dice_rolled = re.findall(r'.*?Re-Rolls\s+Attack\s+Die\s+(\d+).*?and\s+gets\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    def add_defense_dice(self,fss,value):
        dice_added = self.get_dice_added(value)
        dice = Dice(dice_type=DiceType.GREEN,
                    dice_face=dice_added,
                    dice_origination=Dice.ADDED)
        evade_throw = self.current_throw
        results = evade_throw.results
        dice_number = len(results)+1
        result = DiceThrowResult(dice_num=dice_number,
                                           dice=dice,
                                           final_dice=dice)
        results.append(result)

    def add_attack_dice(self, fss, value):
        dice_added = self.get_dice_added(value)
        #this is probably too blissful, but give it a chance!
        dice = Dice(dice_type=DiceType.RED,
                    dice_face=dice_added,
                    dice_origination=Dice.ADDED)
        dice_number = len(self.current_throw.results)+1
        throw_result = DiceThrowResult(dice_num=dice_number, dice=dice, final_dice=dice)
        self.current_throw.results.append(throw_result)

    def process_attack_dice_cancelled(self, value):
        #go through and try to find a dice to be cancelled
        dice_cancelled = self.get_dice_cancelled(value)
        for throw_result in self.current_throw.results:
            if not throw_result.was_cancelled():
                if throw_result.final_dice.is_hit() and dice_cancelled == DiceFace.HIT or\
                   throw_result.final_dice.is_crit() and dice_cancelled == DiceFace.CRIT:
                    self.process_attack_dice_modify(DiceThrowAdjustmentType.CANCELLED,
                                                    throw_result.dice_num,
                                                    dice_cancelled)
                    break


    def process_attack_dice_turn(self, value):
        dice = self.get_attack_dice_changed_by_set(value)
        adjustment_type = DiceThrowAdjustmentType.TURNED
        dice_number = int(dice[0][0])
        dice_value = LogFileParser.face_translate[dice[0][1]]
        self.process_attack_dice_modify(adjustment_type, dice_number, dice_value)

    def process_attack_reroll(self,value):
        dice = self.get_attack_dice_rerolled(value)
        adjustment_type = DiceThrowAdjustmentType.REROLL
        dice_number = int(dice[0][0])
        dice_value = LogFileParser.face_translate[dice[0][1]]
        self.process_attack_dice_modify(adjustment_type, dice_number, dice_value)

    def process_attack_dice_modify(self, adjustment_type, dice_number, dice_value):
        modified_result = self.current_throw.results[dice_number - 1]

        # if there were no adjustments, then the from is just from the base result
        # otherwise its from the last adjustment
        from_dice = None
        if len(modified_result.adjustments) == 0:
            from_dice = modified_result.dice
        else:
            from_dice = modified_result.adjustments[-1].to_dice
        to_dice = Dice(dice_type=DiceType.RED,
                       dice_face=dice_value,
                       dice_origination=from_dice.dice_origination)
        modified_result.final_dice = to_dice
        adjustment = DiceThrowAdjustment(adjustment_type=adjustment_type,
                                         from_dice=from_dice,
                                         to_dice=to_dice)
        modified_result.adjustments.append(adjustment)

    def process_attack_focus(self):
        for dtr in self.current_throw.results:
            if dtr.final_dice.dice_face == DiceFace.FOCUS:
                from_dice = None
                if len(dtr.adjustments) == 0:
                    from_dice       = dtr.dice
                else:
                    from_dice       = dtr.adjustments[-1].to_dice
                to_dice    = Dice(dice_type=DiceType.RED,
                                  dice_face=DiceFace.HIT,
                                  dice_origination=from_dice.dice_origination)
                adjustment = DiceThrowAdjustment(adjustment_type=DiceThrowAdjustmentType.CONVERT,
                                        from_dice=from_dice,
                                        to_dice=to_dice)
                dtr.adjustments.append( adjustment )
                dtr.final_dice = to_dice

    def add_attack_modification(self,game_state,value):
        if self.player_rerolled_attack_dice(value):
            self.process_attack_reroll(value)
        elif self.player_using_focus_token_on_attack(value):
            self.process_attack_focus()
        elif self.player_turned_attack_dice(value):
            self.process_attack_dice_turn(value)
        elif self.player_cancelled_attack_dice(value):
            self.process_attack_dice_cancelled(value)

    def get_defense_dice_rerolled(self, line):
        dice_rolled = re.findall(r'.*?Re-Rolls\s+Defense\s+Die\s+(\d+).*?and\s+gets\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    def get_defense_dice_changed_by_set(self, line):
        dice_rolled = re.findall(r'.*?turns\s+Defense\s+Die\s+(\d+).*?into\s+a\s+\[(.*?)\]', line)
        return dice_rolled

    def get_attack_dice_changed_by_set(self, line):
        dice_rolled = re.findall(r'.*?turns\s+Attack\s+Die\s+(\d+).*?into\s+a\s+\[(.*?)\]', line)
        return dice_rolled


    def add_defense_modification(self,game_state,value):
        if self.player_using_focus_token_on_defense(value):
            self.process_defense_focus()
        elif self.player_rerolled_defense_dice(value):
            self.process_defense_reroll(value)
        elif self.player_turned_defense_dice(value):
            self.process_defense_dice_turn(value)

    def process_defense_focus(self):
        for dtr in self.current_throw.results:
            if dtr.final_dice.dice_face == DiceFace.FOCUS:
                from_dice = None
                if len(dtr.adjustments) == 0:
                    from_dice       = dtr.dice
                else:
                    from_dice       = dtr.adjustments[-1].to_dice
                to_dice    = Dice(dice_type=DiceType.GREEN,
                                  dice_face=DiceFace.EVADE,
                                  dice_origination=from_dice.dice_origination)
                adjustment = DiceThrowAdjustment(adjustment_type=DiceThrowAdjustmentType.CONVERT,
                                        from_dice=from_dice,
                                        to_dice=to_dice)
                dtr.adjustments.append( adjustment )
                dtr.final_dice = to_dice

    def process_defense_dice_turn(self, value):
        dice = self.get_defense_dice_changed_by_set(value)
        adjustment_type = DiceThrowAdjustmentType.CONVERT
        self.process_defense_dice_modification( dice, adjustment_type)

    def process_defense_reroll(self,value):
        dice = self.get_defense_dice_rerolled(value)
        adjustment_type = DiceThrowAdjustmentType.REROLL
        self.process_defense_dice_modification( dice, adjustment_type)

    def process_defense_dice_modification(self,dice,adjustment_type):
        dice_number = int(dice[0][0])
        dice_value = LogFileParser.face_translate[dice[0][1]]

        modified_result = self.current_throw.results[ dice_number - 1 ]

        from_dice = None
        if len(modified_result.adjustments) == 0:
            from_dice       = modified_result.dice
        else:
            from_dice       = modified_result.adjustments[-1].to_dice

        to_dice         = Dice(dice_type=DiceType.GREEN,
                               dice_face=dice_value,
                               dice_origination=from_dice.dice_origination)
        modified_result.final_dice = to_dice
        adjustment = DiceThrowAdjustment(adjustment_type=adjustment_type,
                                        from_dice=from_dice,
                                        to_dice=to_dice)
        modified_result.adjustments.append( adjustment )
