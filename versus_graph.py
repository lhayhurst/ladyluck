
class VersusGraph:
    def __init__(self,game):
        self.game = game

    def plot(self):

        player1_score = []
        player2_score = []

        score = self.game.game_tape.cumulative_score
        print "foo"
