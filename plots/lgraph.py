
import StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt

class LuckGraphs:

    def __init__(self, game):
        fig = plt.figure(1, figsize=(15, 8))
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_title("Advantage ({0} red, {1} green)".format(game.player1, game.player2))
        #create the bar chart of luck "advantage"
        data = []
        player1_luck = [x + y for x, y in zip(game.player1_stats.red_turns, game.player1_stats.green_turns)]
        player2_luck = [x + y for x, y in zip(game.player2_stats.red_turns, game.player2_stats.green_turns)]
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
        ax1.set_ylabel("Luck")
        ax1.grid(True)

        ax2 = fig.add_subplot(2, 2, 2)
        ax2.set_title("Damage ({0} red, {1} green)".format(game.player1, game.player2))

        ax2.plot(game.player1_num_uncancelled_hits(), linewidth=3.0, color='r')
        ax2.plot(game.player2_num_uncancelled_hits(), linewidth=3.0, color='g')
        ax2.grid(True)
        ax2.set_xlabel("Attack sets")
        ax2.set_ylabel("Num uncancelled hits or crits")


        ax3 = fig.add_subplot(2, 2, 3)
        ax3.plot(player1_luck, linewidth=3.0, color='b')
        ax3.grid(True)
        ax3.set_xlabel("Attack sets")
        ax3.set_ylabel("Attack Luck")
        ax3.set_title("{0} attack vs {1} defense".format(game.player1, game.player2))

        ax4 = fig.add_subplot(2, 2, 4)
        ax4.plot(player2_luck, linewidth=3.0, color='b')
        ax4.grid(True)
        ax4.set_xlabel("Attack sets")
        ax4.set_ylabel("Attack Luck")
        ax4.set_title("{0} attack versus {1} defense".format(game.player2, game.player1))

        self.fig = fig


    def get_output(self):
        self.fig.tight_layout()

        canvas = FigureCanvas(self.fig)
        output = StringIO.StringIO()
        canvas.print_png( output )
        plt.close(self.fig)
        self.fig = None
        return output



