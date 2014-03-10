
import StringIO
from stats import LuckStats
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class LuckGraphs:
    def __init__(self, turns):

        self.player2_num_uncancelled_hits = [0]
        self.player1_num_uncancelled_hits = [0]
        self.player1_stats = None
        self.player2_stats = None
        self.player1 = None
        self.player2 = None
        self.turns = turns

        for turn in turns:
            if self.player1 is None:
                self.player1 = turn.attacking_player
                self.player1_stats = LuckStats(self.player1)
            elif self.player1 != None and self.player2 is None and turn.attacking_player != self.player1:
                self.player2 = turn.attacking_player
                self.player2_stats = LuckStats(self.player2)

        self.populate_stats()
        self.create_graphs()

    def populate_stats(self):

        for turn in self.turns:
            if not turn.was_likely_an_asteroid_roll():
                for roll in turn.attack_rolls:
                    if roll.player == self.player1:
                        self.player1_stats.add_roll(roll, 'Attack')
                        self.player1_stats.add_attack_luck_record()
                    elif roll.player == self.player2:
                        self.player2_stats.player = roll.player
                        self.player2_stats.add_roll(roll, 'Attack')
                        self.player2_stats.add_attack_luck_record()
                    else:
                        RuntimeError("third player detected??")
                for roll in turn.defense_rolls:
                    if roll.player == self.player1:
                        self.player1_stats.add_roll(roll, 'Defend')
                        self.player1_stats.add_defense_luck_record()
                    elif roll.player == self.player2:
                        self.player2_stats.add_roll(roll, 'Defend')
                        self.player2_stats.add_defense_luck_record()
                    else:
                        RuntimeError("third player detected?")
            if not turn.was_likely_an_asteroid_roll():
                if turn.attacking_player == self.player1:
                    self.player1_num_uncancelled_hits.append(
                        turn.num_uncancelled_hits() + self.player1_num_uncancelled_hits[-1])
                    self.player2_num_uncancelled_hits.append(self.player2_num_uncancelled_hits[-1])
                else:
                    self.player2_num_uncancelled_hits.append(
                        turn.num_uncancelled_hits() + self.player2_num_uncancelled_hits[-1])
                    self.player1_num_uncancelled_hits.append(self.player1_num_uncancelled_hits[-1])
            else:  #flip it.  asteroids are bad for the attacking player, good for the defending player.
                if turn.attacking_player == self.player1:
                    self.player2_num_uncancelled_hits.append(
                        turn.num_uncancelled_hits() + self.player2_num_uncancelled_hits[-1])
                    self.player1_num_uncancelled_hits.append(self.player1_num_uncancelled_hits[-1])
                else:
                    self.player1_num_uncancelled_hits.append(
                        turn.num_uncancelled_hits() + self.player1_num_uncancelled_hits[-1])
                    self.player2_num_uncancelled_hits.append(self.player2_num_uncancelled_hits[-1])

            self.player1_stats.add_attack_set_luck()
            self.player2_stats.add_attack_set_luck()

    def create_graphs(self):
        fig = plt.figure(1, figsize=(15, 8))
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_title("Advantage ({0} red, {1} green)".format(self.player1, self.player2))
        #create the bar chart of luck "advantage"
        data = []
        player1_luck = [x + y for x, y in zip(self.player1_stats.red_turns, self.player1_stats.green_turns)]
        player2_luck = [x + y for x, y in zip(self.player2_stats.red_turns, self.player2_stats.green_turns)]
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

        ax1.set_xlabel("Turns")
        ax1.set_ylabel("Luck")
        ax1.grid(True)

        ax2 = fig.add_subplot(2, 2, 2)
        ax2.set_title("Damage ({0} red, {1} green)".format(self.player1, self.player2))

        ax2.plot(self.player1_num_uncancelled_hits, linewidth=3.0, color='r')
        ax2.plot(self.player2_num_uncancelled_hits, linewidth=3.0, color='g')
        ax2.grid(True)
        ax2.set_xlabel("Attack sets")
        ax2.set_ylabel("Num uncancelled hits or crits")


        ax3 = fig.add_subplot(2, 2, 3)
        ax3.plot(player1_luck, linewidth=3.0, color='b')
        ax3.grid(True)
        ax3.set_xlabel("Attack sets")
        ax3.set_ylabel("Attack Luck")
        ax3.set_title("{0} attack vs {1} defense".format(self.player1, self.player2))

        ax4 = fig.add_subplot(2, 2, 4)
        ax4.plot(player2_luck, linewidth=3.0, color='b')
        ax4.grid(True)
        ax4.set_xlabel("Attack sets")
        ax4.set_ylabel("Attack Luck")
        ax4.set_title("{0} attack versus {1} defense".format(self.player2, self.player1))

        self.fig = fig


    def get_output(self):
        self.fig.tight_layout()

        canvas = FigureCanvas(self.fig)
        output = StringIO.StringIO()
        canvas.print_png( output )
        plt.close(self.fig)
        self.fig = None
#        plt.clf()
#        plt.cla()
        return output



