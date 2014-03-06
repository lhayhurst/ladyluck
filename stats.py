import re


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

    EVADE_WEIGHT = 0.59375
    GREEN_EYE_WEIGHT = 0.34375
    GREEN_BLANK_WEIGHT = -1.40625


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

    def expected_red_hits(self, total=None):
        t = 0
        if total == None:
            t = self.total_reds
        else:
            t = total
        return t * (3.0 / 8.0)

    def expected_red_misses(self, total=None):
        t = 0
        if total == None:
            t = self.total_reds
        else:
            t = total
        return t * (2.0 / 8.0)

    def expected_red_crits(self, total=None ):
        t = 0
        if total == None:
            t = self.total_reds
        else:
            t = total
        return t * (1.0 / 8.0)

    def expected_red_eyes(self, total = None ):
        t = 0
        if total == None:
            t = self.total_reds
        else:
            t = total
        return t * (2.0 / 8.0)

    def expected_green_evades(self, total=None):
        t = 0
        if total == None:
            t = self.total_greens
        else:
            t = total
        return t * (3.0 / 8.0)

    def expected_green_blanks(self, total=None):
        t = 0
        if total == None:
            t = self.total_greens
        else:
            t = total
        return t * (3.0 / 8.0)

    def expected_green_eyes(self, total=None):
        t = 0
        if total == None:
            t = self.total_greens
        else:
            t = total
        return t * (2.0 / 8.0)

    def print_stats( self ):

        print ("Player {0}".format(self.player) )
        print("RED DICE")
        print ("\tTotal rolls: {0}".format(self.total_reds) )
        print ("\tHits: {0} (Expected: {1})".format( self.red_hits, self.expected_red_hits()) )
        print ("\tCrits: {0} (Expected: {1})".format( self.red_crits, self.expected_red_crits()) )
        print ("\tEyes: {0} (Expected: {1})".format( self.red_eyes, self.expected_red_eyes()) )
        print ("\tBlanks: {0} (Expected: {1})".format( self.red_blanks, self.expected_red_misses()) )

        expected_green_evades = self.expected_green_evades()
        expected_green_blanks = self.expected_green_blanks()
        expected_green_eyes  = self.expected_green_eyes()

        print("GREEN DICE")
        print ("\tTotal rolls: {0}".format(self.total_greens) )
        print ("\tEvades: {0} (Expected: {1})".format( self.green_evades, expected_green_evades) )
        print ("\tEyes: {0} (Expected: {1})".format( self.green_eyes, expected_green_eyes) )
        print ("\tBlanks: {0} (Expected: {1})".format( self.green_blanks, expected_green_blanks) )


    def sub(self, from_text, to_text, text ):
        text = re.sub( from_text, to_text, text, re.M)
        return text

    def print_stats_html(self, player2):

        total_reds = self.total_reds
        total_greens   = self.total_greens


        htmlfile = open( "template.html")
        html     = htmlfile.read()

        html = self.sub( "\$P1", self.player, html )
        html = self.sub( r'\$P2', player2.player, html )
        html = self.sub( r'\$PL1_RED_TOTAL', str(total_reds), html )
        html = self.sub( r'\$PL2_GREEN_TOTAL', str(player2.total_greens), html)
        html = self.sub( r'\$PLAYER_ONE_RED_HIT', str(self.red_hits), html  )
        html = self.sub( r'\$PLAYER1_RED_HITS_EXPECTED', str(self.expected_red_hits()), html )
        html = self.sub( r'\$PLAYER1_RED_CRIT', str(self.red_crits), html)
        html = self.sub( r'\$PL1_CRITS_EXP', str(self.expected_red_crits()), html )
        html = self.sub( r'\$PLAYER2_GREEN_EVADES', str(player2.green_evades), html)

        html = self.sub( r'\$PL1_RED_FOCUS', str(self.red_eyes), html)
        html = self.sub( r'\$RED_FOCUS_EXP_PL1', str(self.expected_red_eyes()), html)
        html = self.sub( r'\$PL2_GREEN_FOCUS', str(player2.green_eyes), html)
        html = self.sub( r'\$GREEN_FOCUS_EXP_PL2', str(player2.expected_green_eyes()), html)

        html = self.sub( r'\$PL1_RED_BLANK', str(self.red_blanks ), html)
        html = self.sub( r'\$RED_BLANK_EXP_PL1', str(self.expected_red_misses()), html)
        html = self.sub( r'\$PL2_GREEN_BLANK', str(player2.green_blanks), html)
        html = self.sub( r'\$GREEN_BLANK_EXP_PL2', str(player2.expected_green_blanks()), html)

        #DO THE OTHER SIDE
        html = self.sub( r'\$PL2_RED_TOTAL', str(player2.total_reds), html )
        html = self.sub( r'\$PL1_GREEN_TOTAL', str(self.total_greens), html)
        html = self.sub( r'\$PLAYER_TWO_RED_HIT', str(player2.red_hits), html  )
        html = self.sub( r'\$PLAYER2_RED_HITS_EXPECTED', str(player2.expected_red_hits()), html )
        html = self.sub( r'\$PLAYER2_RED_CRIT', str(player2.red_crits), html)
        html = self.sub( r'\$PL2_CRITS_EXP', str(player2.expected_red_crits()), html )
        html = self.sub( r'\$PLAYER1_GREEN_EVADES', str(self.green_evades), html)

        html = self.sub( r'\$PL2_RED_FOCUS', str(player2.red_eyes), html)
        html = self.sub( r'\$RED_FOCUS_EXP_PL2', str(player2.expected_red_eyes()), html)
        html = self.sub( r'\$PL1_GREEN_FOCUS', str(self.green_eyes), html)
        html = self.sub( r'\$GREEN_FOCUS_EXP_PL1', str(self.expected_green_eyes()), html)

        html = self.sub( r'\$PL2_RED_BLANK', str(player2.red_blanks ), html)
        html = self.sub( r'\$RED_BLANK_EXP_PL2', str(player2.expected_red_misses()), html)
        html = self.sub( r'\$PL1_GREEN_BLANK', str(self.green_blanks), html)
        html = self.sub( r'\$GREEN_BLANK_EXP_PL1', str(self.expected_green_blanks()), html)

        return html

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

    def add_turn_luck(self):
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

    def add_dice_set(self, set_num, dice_roll_set):

        for roll in dice_roll_set.attack_rolls:
            self.dice_stats.add_roll( roll, 'Attack')
            self.add_attack_luck_record()
        for roll in dice_roll_set.defense_rolls:
            self.dice_stats.add_roll( roll, 'Defend')
            self.add_defense_luck_record()

    def add_roll(self, result, type):
        self.dice_stats.add_roll(result, type)