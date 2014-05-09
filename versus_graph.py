
class VersusGraph:
    def __init__(self,game):
        self.game = game
        self.p1   = game.game_players[0]
        self.p2   = game.game_players[1]

    def plot(self):

        player1_red_score = self.game.game_tape.red_scores( self.p1 )
        player2_red_score = self.game.game_tape.red_scores( self.p2 )
