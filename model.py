import os
import re
import uuid
import shutil
from werkzeug.utils import secure_filename
from lgraph import LuckGraphs
from enum import Enum
import time

class DiceRoll:
    def __init__(self, result, num, player ):
        self.player = player
        self.values = []
        self.num = num
        self.values.append( result )

    HIT = "Hit"
    CRIT = "Crit"
    BLANK = "Blank"
    FOCUS = "Focus"
    EVADE = "Evade"


    def was_focus_reroll(self):
        return len(self.values) == 2 and \
               self.values[0] == DiceRoll.FOCUS

    def value_is(self, value):
        return self.values[-1] == value

    def is_crit(self):
        return self.value_is(DiceRoll.CRIT)

    def is_hit(self):
        return self.value_is(DiceRoll.HIT)

    def is_evade(self):
        return self.value_is(DiceRoll.EVADE)

    def add_value(self, value):
        self.values.append(value)

    def get_result(self):
        return self.values[-1]

    def was_modified(self):
        return len(self.values) > 1

    def started_out_as(self):
        return self.values[0]

class AttackSet:
    def __init__(self, attacking_player, defending_player ):
        self.attack_rolls  = []
        self.defense_rolls = []
        self.attacking_player = attacking_player
        self.defending_player = defending_player

    def num_uncancelled_hits(self):
        count = 0
        for roll in self.attack_rolls:
            if roll.is_hit() or roll.is_crit():
                count = count + 1
        for roll in self.defense_rolls:
            if roll.is_evade():
                count = count - 1
        if count < 0:
            count = 0
        return count

    def add_attack_roll(self, roll):
        if self.attacking_player == None:
            self.attacking_player = roll.player
        self.attack_rolls.append( roll )

    def add_defense_roll(self, roll):
        if self.defending_player == None:
            self.defending_player = roll.player
        self.defense_rolls.append(roll)

    def get_rolls(self):
        return self.rolls

    def add_attack_reroll(self, dice_num, dice_value ):
        roll = self.attack_rolls[ int(dice_num) - 1 ]
        roll.add_value( dice_value )

    def add_defense_reroll(self, dice_num, dice_value ):
        roll = self.defense_rolls[ int(dice_num) - 1 ]
        roll.add_value( dice_value )

    def was_likely_an_asteroid_roll(self):
        return len(self.attack_rolls) == 1 and len( self.defense_rolls ) == 0

class GameTapeEntry:
    def __init__(self, player, round_number, game_state, attack_set_number, entry_type, dice_type, dice_num, dice_face):
        self.player = player
        self.round_number = round_number
        self.game_state = game_state
        self.attack_set_number = attack_set_number
        self.entry_type = entry_type
        self.dice_type = dice_type
        self.dice_num  = dice_num
        self.dice_face = dice_face

class GameTape:
    def __init__(self):
        self.tape = []
        self.player1 = None
        self.player2 = None

    def add(self, entry):
        self.tape.append( entry )
        if self.player1 == None:
            self.player1 = entry.player
        if self.player1 != None and self.player2 == None and self.player1 != entry.player:
            self.player2 = entry.player

    def num_entries(self):
        return len(self.tape)

class Game:
    def __init__(self, persistence_dir):

        self.game_date = time.strftime("%m-%d-%Y")
        self.persistence_dir = persistence_dir
        self.game_id = str(uuid.uuid4())
        self.player1 = None
        self.player2 = None
        self.winner = None
        self.game_tape = None

    def player1_dice_stats(self):
        return self.player1_stats.dice_stats

    def player2_dice_stats(self):
        return self.player2_stats.dice_stats

    def get_graph_image(self):
        return self.image_path

    def run_the_tape(self, game_tape, winner, parser):
        self.winner = winner
        self.game_tape = game_tape
        parser.read_input_from_string(game_tape)
        parser.run_finite_state_machine()

    def create_and_stash_graphs(self):
        graphs = LuckGraphs(self)
        output = graphs.get_output()
        output.seek(0)
        filename = secure_filename( self.game_id + '.png')
        full_pwd = os.path.join( self.persistence_dir, filename)
        self.image_path = full_pwd
        fd = open( full_pwd, 'w')
        shutil.copyfileobj( output, fd )

    def player1_num_uncancelled_hits(self):
        return self.player1_stats.get_num_uncancelled_hits()

    def player2_num_uncancelled_hits(self):
        return self.player2_stats.get_num_uncancelled_hits()

    def populate_stats(self, attack_sets):

        for attack_set in attack_sets:
            if self.player1 is None:
                self.player1 = attack_set.attacking_player
                self.player1_stats = LuckStats(self.player1)
            elif self.player1 != None and self.player2 is None and attack_set.attacking_player != self.player1:
                self.player2 = attack_set.attacking_player
                self.player2_stats = LuckStats(self.player2)


        for attack_set in attack_sets:
            if not attack_set.was_likely_an_asteroid_roll():
                for roll in attack_set.attack_rolls:
                    if roll.player == self.player1:
                        self.player1_stats.add_roll(roll, 'Attack')
                        self.player1_stats.add_attack_luck_record()
                    elif roll.player == self.player2:
                        self.player2_stats.player = roll.player
                        self.player2_stats.add_roll(roll, 'Attack')
                        self.player2_stats.add_attack_luck_record()
                    else:
                        RuntimeError("third player detected??")
                for roll in attack_set.defense_rolls:
                    if roll.player == self.player1:
                        self.player1_stats.add_roll(roll, 'Defend')
                        self.player1_stats.add_defense_luck_record()
                    elif roll.player == self.player2:
                        self.player2_stats.add_roll(roll, 'Defend')
                        self.player2_stats.add_defense_luck_record()
                    else:
                        RuntimeError("third player detected?")
            if not attack_set.was_likely_an_asteroid_roll():
                if attack_set.attacking_player == self.player1:
                    self.player1_stats.add_uncancelled_hit(attack_set.num_uncancelled_hits())
                    self.player2_stats.no_uncancelled_hit()
                else:
                    self.player2_stats.add_uncancelled_hit(attack_set.num_uncancelled_hits())
                    self.player1_stats.no_uncancelled_hit()

            self.player1_stats.add_attack_set_luck()
            self.player2_stats.add_attack_set_luck()


class DiceStats:
    def __init__(self, player):

        self.player       = player
        self.total_reds   = 0
        self.total_greens = 0

        self.red_hits     = 0
        self.red_blanks   = 0
        self.red_eyes     = 0
        self.red_crits    = 0

        self.green_evades = 0
        self.green_blanks = 0
        self.green_eyes   = 0

        self.green_luck   = []
        self.red_luck     = []

        self.num_red_focuses_converted = 0
        self.num_green_focuses_converted = 0


    def set_num_red_focuses_converted(self, count):
        self.num_red_focuses_converted = count

    def red_focuses_converted(self):
        return self.num_red_focuses_converted

    def set_num_green_focuses_converted(self, count):
        self.num_green_focuses_converted = count

    def green_focuses_converted(self):
        return self.num_green_focuses_converted


    def red_hit_differential(self):
        return self.red_hits - self.expected_red_hits()

    def red_crit_differential(self):
        return self.red_crits - self.expected_red_crits()

    def red_focus_differential(self):
        return self.red_eyes - self.expected_red_eyes()

    def red_blank_differential(self):
        return self.expected_red_misses() - self.red_blanks

    def green_evade_differential(self):
        return self.green_evades - self.expected_green_evades()

    def green_eyes_differential(self):
        return self.green_eyes - self.expected_green_eyes()

    def green_blank_differential(self):
        return self.expected_green_blanks() - self.green_blanks



    HIT_WEIGHT = 1.0
    CRIT_WEIGHT = 1.25
    RED_EYE_WEIGHT = .5
    RED_BLANK_WEIGHT = 0

    EVADE_WEIGHT = 1
    GREEN_EYE_WEIGHT = 0.75
    GREEN_BLANK_WEIGHT = 0


    def add_roll(self, roll, type):
        if type == 'Attack':
            self.total_reds += 1
            if roll.get_result() == 'Hit':
                self.red_hits += 1
            elif roll.get_result() == 'Crit':
                self.red_crits += 1
            elif roll.get_result() == 'Focus':
                self.red_eyes += 1
            elif roll.get_result() == 'Blank':
                self.red_blanks += 1
            else:
                RuntimeError ("unknown dice type, wtf?!")
        elif type == 'Defend':
            self.total_greens += 1
            if roll.get_result() == 'Evade':
                self.green_evades += 1
            elif roll.get_result() == 'Focus':
                self.green_eyes += 1
            elif roll.get_result() == 'Blank':
                self.green_blanks += 1
            else:
                RuntimeError ("unknown dice type, wtf?!")

    def expected_red_hits(self):
        t = self.total_reds
        return t * (3.0 / 8.0)

    def expected_red_misses(self):
        t = self.total_reds
        return t * (2.0 / 8.0)

    def expected_red_crits(self ):
        t = self.total_reds
        return t * (1.0 / 8.0)

    def expected_red_eyes(self):
        t = self.total_reds
        return t * (2.0 / 8.0)

    def expected_green_evades(self):
        t = self.total_greens
        return t * (3.0 / 8.0)

    def expected_green_blanks(self):
        t = self.total_greens
        return t * (3.0 / 8.0)

    def expected_green_eyes(self ):
        t = self.total_greens
        return t * (2.0 / 8.0)

    def sub(self, from_text, to_text, text ):
        text = re.sub( from_text, to_text, text, re.M)
        return text


class LuckStats:

    def __init__(self, player):
        self.dice_stats = DiceStats(player)
        self.player     = player
        self.red_luck = []
        self.green_luck = []
        self.green_luck.append(0)
        self.red_luck.append(0)
        self.red_turns = []
        self.green_turns = []
        self.num_uncancelled_hits = [0]


    def get_num_uncancelled_hits(self):
        return self.num_uncancelled_hits

    def add_uncancelled_hit(self, count):
        self.num_uncancelled_hits.append( count + self.num_uncancelled_hits[-1])

    def no_uncancelled_hit(self):
        self.num_uncancelled_hits.append(self.num_uncancelled_hits[-1])


    def add_attack_set_luck(self):
        self.red_turns.append( self.red_luck[-1] )
        self.green_turns.append( self.green_luck[-1])


    def add_defense_luck_record(self):

        exp_evades         = self.dice_stats.expected_green_evades()
        evade_dev          = self.dice_stats.green_evades - exp_evades
        weighted_evade_dev = evade_dev * DiceStats.EVADE_WEIGHT

        exp_focus          = self.dice_stats.expected_green_eyes()
        focus_dev          = self.dice_stats.green_eyes - exp_focus
        weighted_focus_dev = focus_dev * DiceStats.GREEN_EYE_WEIGHT

        exp_blank          = self.dice_stats.expected_green_blanks()
        blank_dev          = self.dice_stats.green_blanks - exp_blank
        weighted_blank_dev = blank_dev * DiceStats.GREEN_BLANK_WEIGHT

        luck = weighted_evade_dev + weighted_focus_dev + weighted_blank_dev

        self.green_luck.append(luck)

    def add_attack_luck_record(self):

        exp_hits         = self.dice_stats.expected_red_hits()
        hit_dev          = self.dice_stats.red_hits - exp_hits
        weighted_hit_dev = hit_dev * DiceStats.HIT_WEIGHT

        exp_crits         = self.dice_stats.expected_red_crits()
        crit_dev          = self.dice_stats.red_crits - exp_crits
        weighted_crit_dev = crit_dev * DiceStats.CRIT_WEIGHT

        exp_focus          = self.dice_stats.expected_red_eyes()
        focus_dev          = self.dice_stats.red_eyes - exp_focus
        weighted_focus_dev = focus_dev * DiceStats.RED_EYE_WEIGHT

        exp_blank          = self.dice_stats.expected_red_misses()
        blank_dev          = self.dice_stats.red_blanks - exp_blank
        weighted_blank_dev = blank_dev * DiceStats.RED_BLANK_WEIGHT

        luck = weighted_hit_dev + weighted_crit_dev + weighted_focus_dev + weighted_blank_dev

        self.red_luck.append(luck)

    def add_roll(self, result, type):
        self.dice_stats.add_roll(result, type)

    def add_dice_set(self, set_num, set):

        for roll in set.attack_rolls:
            self.dice_stats.add_roll( roll, 'Attack')
            self.add_attack_luck_record()
        for roll in set.defense_rolls:
            self.dice_stats.add_roll( roll, 'Defend')
            self.add_defense_luck_record()


    def last_attack_set_red_luck(self):
        return self.red_luck[-1]

    def last_attack_set_green_luck(self):
        return self.green_luck[-1]



