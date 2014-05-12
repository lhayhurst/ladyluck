import StringIO

import matplotlib
# If you want to use a different backend, replace Agg with
# Cairo, PS, SVG, GD, Paint etc.
# Agg stands for "antigrain rendering" and produces PNG files
#matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from persistence import DiceType


class LuckPlot:

    def __init__(self,game, p1, dice_type):
        self.game      = game
        self.p1        = game.get_player_by_id(p1)
        self.game_tape = game.game_tape
        self.dice_type = DiceType.from_string(dice_type)

    def plot(self):

        init_pl_data = []
        adjusted_pl_data = []
        line_color = None

        if self.dice_type == DiceType.RED:
            init_pl_data     = self.game_tape.initial_red_scores(self.p1)
            adjusted_pl_data = self.game_tape.final_red_scores( self.p1 )
            line_color = 'r'
        else:
            init_pl_data     = self.game_tape.initial_green_scores(self.p1)
            adjusted_pl_data = self.game_tape.final_green_scores( self.p1 )
            line_color = 'g'

        fig = plt.figure(figsize=(6,2.5))
        ax = fig.add_subplot(111)
        ax.plot( adjusted_pl_data, linewidth=3.0, color=line_color)
        ax.plot( init_pl_data, linewidth=3.0, linestyle='--', color='b'  )

        ax.grid(True)
        ax.set_xlabel("Attack sets")
        ax.set_ylabel("Score")

        output = StringIO.StringIO()
        canvas = FigureCanvas( fig  )
        canvas.print_png( output )
        return output
