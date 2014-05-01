import StringIO
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class TapeGraph:
    def __init__(self, game, game_tape):
        self.game_tape = game_tape

        self.p1_attacks = []
        self.p1_defense = []
        self.p2_attacks = []
        self.p2_defense = []

        player1 = game.game_players[0]
        player2 = game.game_players[1]
        x_axis = []

        i = 1
        for aset in game_tape.attack_sets:
            x_axis.append(i)
            i = i + 1
            if aset.attacking_player == player1.name:
                self.p1_attacks.append( aset.total_attack_end_luck())
                self.p2_attacks.append( None)
                if aset.defending_player == None:
                    self.p2_defense.append(0)
                    self.p1_defense.append(0)
                else:
                    self.p2_defense.append( aset.total_defense_end_luck() )
                    self.p1_defense.append(0)
            elif aset.attacking_player == player2.name:
                self.p2_attacks.append( aset.total_attack_end_luck())
                self.p1_attacks.append(0)
                if aset.defending_player == None:
                    self.p1_defense.append(0)
                    self.p2_defense.append(0)
                else:
                    self.p1_defense.append( aset.total_defense_end_luck() )
                    self.p2_defense.append(0)

        circle1=plt.Circle((0,0),.2,color='r', fillstyle=False)
        circle2=plt.Circle((.5,.5),.2,color='b', fillstyle=None)
        circle3=plt.Circle((1,1),.2,color='g',clip_on=False)
        fig = plt.gcf()
        fig.gca().add_artist(circle1)
        fig.gca().add_artist(circle2)
        fig.gca().add_artist(circle3)
        plt.show()