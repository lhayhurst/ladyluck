import os

from flask import Flask, render_template, request, url_for, redirect, Response, make_response

from game_summary_stats import GameTape
from parser import LogFileParser
from persistence import PersistenceManager, Game
from sparkplot import Sparkplot


UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = set( ['png'])

app    = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
here = os.path.dirname(__file__)
static_dir = os.path.join( here, app.config['UPLOAD_FOLDER'] )
db = PersistenceManager()

ADMINS = ['sozinsky@gmail.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1', 'server-error@pythonanywhere.com',
    ADMINS, 'Ladyluck Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


def get_all_games():
    ret = []
    games = db.get_games()

    for game in games:
        p1 = game.game_players[0]
        p2 = game.game_players[1]
        url_text = "{0} vs {1} ({2})".format(p1.name, p2.name, game.game_played_time)
        ret.append( { 'text' : url_text, 'guid' : 'game?id=' + str(game.id)})
    return ret


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/games" )
def games():
    games = get_all_games()
    return( render_template('games.html', games=games) )


@app.route('/new', methods=['GET'])
def new():
  return render_template('new.html')

#redirect '/' to new
@app.route('/')
def index():
    return redirect(url_for('new') )

@app.route('/add_game', methods=['POST'])
def add_game():
    tape  = request.form['chatlog']
    winner = request.form['winner']
    if len(tape) == 0:
        return redirect(url_for('new'))

    parser = LogFileParser()
    parser.read_input_from_string(tape)
    parser.run_finite_state_machine()

    game = Game( parser.get_players())

    p1 = game.game_players[0]
    p2 = game.game_players[1]

    winning_player = None
    if winner is not None:
        if winner == p1.name:
            winning_player = p1
        elif winner == p2.name:
            winning_player = p2
    game.game_winner = winning_player

    for throw_result in parser.game_tape:
        game.game_throws.append(throw_result)


    db.session.add(game)
    db.session.commit()

    return redirect( url_for('game', id=str(game.id)) )

def get_game_tape_text(game, make_header=True):

    rows = []
    if make_header:
        rows.append( ['game_id', 'player_name', 'throw_id', 'attack_set_num', 'dice_num', 'roll_type', 'dice_color', 'dice_result'] )

    for throw in game.game_throws:
        for result in throw.results:
            row = [ str(game.id), throw.player.name, str(throw.id), str(throw.attack_set_num), str(result.dice_num), \
                    throw.throw_type.description, result.dice.dice_type.description, result.dice.dice_face.description]
            rows.append(row)
        for result in throw.results:
            for a in result.adjustments:
                arow = [ str(game.id), throw.player.name, str(throw.id), str(throw.attack_set_num), str(result.dice_num), \
                        a.adjustment_type.description, a.to_dice.dice_type.description, a.to_dice.dice_face.description]
                rows.append(arow)

    return rows

@app.route('/download-game')
def download_game():
    game_id = str(request.args.get('id'))
    game = db.get_game(game_id)
    def generate():
        rows = get_game_tape_text(game)
        for r in rows:
           yield ",".join(r) + '\n'
    return Response(generate(), mimetype='text/csv')

@app.route('/game')
def game():
    id = str(request.args.get('id'))
    game = db.get_game(id)
    if game == None:
        return redirect(url_for('add_game'))

    player1 = game.game_players[0]
    player2 = game.game_players[1]

    winning_player = "Unknown"
    if game.game_winner is not None:
        winning_player = game.game_winner.name

    #summary_stats = GameSummaryStats(game)
    game_tape = GameTape(game)
    game_tape.score()

    return render_template( 'game_summary.html',
                            game=game,
                            player1=player1,
                            player2=player2,
                            winner=winning_player,
                            game_tape=game_tape )

@app.route('/sparkline')
def sparkline():
    id = str(request.args.get('game_id'))
    game = db.get_game(id)
    player_name = str(request.args.get('player'))

    sparkline = Sparkplot(data=game.game_tape.unmodified_attack_data( player_name ), label_min=True, label_max=True )
    output = sparkline.plot_sparkline()
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == '__main__':
    app.debug = True
    app.run()
