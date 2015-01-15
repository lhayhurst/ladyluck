import StringIO
import matplotlib
matplotlib.use('AGG')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from persistence import DiceType

FIGSIZE = (5,2)


class LuckPlot:

    def __init__(self,game, p1, plot_against_player, dice_type):
        self.game      = game
        self.p1        = p1
        self.p2 = plot_against_player
        self.game_tape = game.game_tape
        self.dice_type = dice_type

    def plot(self):

        init_pl_data = []
        adjusted_pl_data = []
        line_color = None

        min_y = 0
        max_y = 0
        init_p1_data = None
        init_p2_data = None
        adjusted_p1_data = None
        adjusted_p2_data = None

        if self.dice_type == DiceType.RED:
            init_pl_data     = self.game_tape.initial_red_scores(self.p1)
            adjusted_pl_data = self.game_tape.final_red_scores( self.p1 )
            init_p2_data     = self.game_tape.initial_red_scores(self.p2)
            adjusted_p2_data = self.game_tape.final_red_scores( self.p2 )
            line_color = 'r'
        else:
            init_pl_data     = self.game_tape.initial_green_scores(self.p1)
            adjusted_pl_data = self.game_tape.final_green_scores( self.p1 )
            init_p2_data     = self.game_tape.initial_green_scores(self.p2)
            adjusted_p2_data = self.game_tape.final_green_scores( self.p2 )
            line_color = 'g'

        p1_init_min = min( init_pl_data )
        p2_init_min = min( init_p2_data )
        p1_adjusted_max = max(adjusted_pl_data)
        p2_adjusted_max = max(adjusted_p2_data)

        min_y = min( [p1_init_min, p2_init_min, p1_adjusted_max, p2_adjusted_max  ])
        max_y = max( [p1_init_min, p2_init_min, p1_adjusted_max, p2_adjusted_max  ])

        fig = plt.figure(figsize=FIGSIZE)
        ax = fig.add_subplot(111)
        ax.set_ylim( min_y, max_y)
        ax.plot( adjusted_pl_data, linewidth=3.0, color=line_color)
        ax.plot( init_pl_data, linewidth=3.0, linestyle='--', color='b'  )

        ax.grid(True)

        output = StringIO.StringIO()
        fig.savefig(output, format='png')
        plt.close()
        data = output.getvalue().encode('base64')
        return data

class DamagePlot:

    def __init__(self,game ):
        self.game            = game
        self.game_tape = game.game_tape

    def plot(self):


        p1 = self.game.game_players[0]
        p2 = self.game.game_players[1]

        p1_damage = self.game_tape.damage(p1)
        p2_damage = self.game_tape.damage(p2)

        fig = plt.figure(figsize=FIGSIZE)
        ax = fig.add_subplot(111)
        ax.plot( p1_damage, linewidth=3.0, color='r')
        ax.plot( p2_damage, linewidth=3.0, color='g'  )

        ax.grid(True)

        output = StringIO.StringIO()
        fig.savefig(output, format='png')
        plt.close()
        data = output.getvalue().encode('base64')
        return data


class VersusPlot:

    def __init__(self,game, attacker, defender ):
        self.game            = game
        self.attacker        = attacker
        self.defender        = defender
        self.game_tape = game.game_tape

    def plot(self):


        p1_initial_attack   = self.game_tape.initial_red_scores( self.attacker )
        p1_adjusted_attack  = self.game_tape.final_red_scores( self.attacker )
        p2_initial_defense  = self.game_tape.initial_green_scores( self.defender )
        p2_adjusted_defense = self.game_tape.final_green_scores( self.defender )

        initial_attack  = [x - y for x, y in zip(p1_initial_attack, p2_initial_defense)]
        adjusted_attack = [x - y for x, y in zip(p1_adjusted_attack, p2_adjusted_defense)]

        fig = plt.figure(figsize=FIGSIZE)
        ax = fig.add_subplot(111)
        ax.plot( adjusted_attack, linewidth=3.0, color='r')
        ax.plot( initial_attack, linewidth=3.0, linestyle='--', color='b'  )

        ax.grid(True)

        output = StringIO.StringIO()
        fig.savefig(output, format='png')
        plt.close()
        data = output.getvalue().encode('base64')
        return data

class AdvantagePlot:

    def __init__(self,game, use_initial):
        self.game        = game
        self.use_initial = use_initial
        self.p1          = game.game_players[0]
        self.p2          = game.game_players[1]
        self.game_tape   = game.game_tape


    def plot(self):

        player1_red_score = []
        player1_green_score = []
        player2_red_score = []
        player2_green_score = []



        if self.use_initial == 0:
            player1_red_score   = self.game_tape.initial_red_scores( self.p1 )
            player1_green_score = self.game_tape.initial_green_scores( self.p1 )
            player2_red_score = self.game_tape.initial_red_scores( self.p2 )
            player2_green_score = self.game_tape.initial_green_scores( self.p2 )
        else:
            player1_red_score   = self.game_tape.final_red_scores( self.p1 )
            player1_green_score = self.game_tape.final_green_scores( self.p1 )
            player2_red_score = self.game_tape.final_red_scores( self.p2 )
            player2_green_score = self.game_tape.final_green_scores( self.p2 )

        fig = plt.figure(figsize=FIGSIZE)
        ax1 = fig.add_subplot(111)

        player1_luck = [x + y for x, y in zip( player1_red_score, player1_green_score)]
        player2_luck = [x + y for x, y in zip(player2_red_score, player2_green_score)]
        luck_swing = [x - y for x, y in zip(player1_luck, player2_luck)]

        x_axis_values = []
        i = 1
        player1_adv = []
        player2_adv = []

        for ls in luck_swing:
            x_axis_values.append(i)
            if ls > 0:
                player1_adv.append(ls)
                player2_adv.append(0)
            elif ls == 0:
                player1_adv.append(0)
                player2_adv.append(0)
            else:
                player1_adv.append(0)
                player2_adv.append(ls)
            i += 1

        ax1.bar(x_axis_values, player1_adv, color='r')
        ax1.bar(x_axis_values, player2_adv, color='g')

        ax1.grid(True)

        output = StringIO.StringIO()
        fig.savefig(output, format='png')
        plt.close()

        data = output.getvalue().encode('base64')
        return data

