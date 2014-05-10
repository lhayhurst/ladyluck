import StringIO

import matplotlib
# If you want to use a different backend, replace Agg with
# Cairo, PS, SVG, GD, Paint etc.
# Agg stands for "antigrain rendering" and produces PNG files
#matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt

class VersusGraph:
    def __init__(self,game):
        self.game      = game
        self.p1        = game.game_players[0]
        self.p2        = game.game_players[1]
        self.game_tape = game.game_tape

    def plot(self):

        player1_red_score   = self.game_tape.final_red_scores( self.p1 )
        player1_green_score = self.game_tape.final_green_scores( self.p1 )
        player2_red_score = self.game_tape.final_red_scores( self.p2 )
        player2_green_score = self.game_tape.final_green_scores( self.p2 )

        fig = plt.figure(1, figsize=(15, 8))
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_title("Advantage ({0} red, {1} green)".format(self.p1.name, self.p2.name))

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

        ax1.set_xlabel("Attack sets")
        ax1.set_ylabel("Net advantage score")
        ax1.grid(True)

        ax2 = fig.add_subplot(2, 2, 3)
        ax2.plot( player2_red_score, label="Final attack score", linewidth=3.0, color='b')
        ax2.plot( self.game_tape.initial_red_scores(self.p2), linewidth=3.0, linestyle='--', color='b', label="Initial attack score" )
        #ax2.plot( player1_green_score, linewidth=3.0, color='g')
        #ax2.plot( self.game_tape.initial_green_scores(self.p1), linewidth=3.0, color='g', ls='--' )

        ax2.grid(True)
        ax2.set_xlabel("Attack sets")
        ax2.set_ylabel("Score score")
        ax1.set_title("{0} Red dice adjusted and unadjusted scores")

        output = StringIO.StringIO()
        canvas = FigureCanvas( fig  )
        canvas.print_png( output )
        return output
