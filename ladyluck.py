import os
from flask import Flask, render_template, request, url_for, redirect, Response
from parser import LogFileParser
from persistence import PersistenceManager, Player, GameRoll, Game


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

    game_tape = parser.game_tape.tape
    p1 = Player(name=parser.game_tape.player1)
    p2 = Player(name=parser.game_tape.player2)
    game = Game(p1, p2)

    db.session.add(game)
    db.session.commit()

    for gt in game_tape:
        player_id = None
        if gt.player == p1.name:
            player_id = p1.id
        elif gt.player == p2.name:
            player_id = p2.id

        game_id = game.id
        dice = db.get_dice(gt.dice_type, gt.dice_face)

        db.session.add(GameRoll( player_id=player_id,
                        game_id=game_id,
                        roll_type=gt.entry_type,
                        dice_id=dice.id,
                        attack_set_num=gt.attack_set_number,
                        dice_num=gt.dice_num ))
    db.session.commit()
    return redirect( url_for('game', id=str(game.id)) )

@app.route('/download-game')
def download_game():
    game_id = str(request.args.get('id'))
    game = db.get_game(game_id)
    def generate():
        yield ",".join([ 'game_id', 'player_name', 'attack_set_num', 'dice_num', 'roll_type', 'dice_color', 'dice_result']) + '\n'
        for roll in game.game_roll:
            row = [ str(game_id), roll.player.name, str(roll.attack_set_num), str(roll.dice_num),
                    roll.roll_type.description, roll.dice.dice_type.description, roll.dice.dice_face.description]
            yield ",".join(row) + '\n'
    return Response(generate(), mimetype='text/csv')

@app.route('/game')
def game():
    id = str(request.args.get('id'))
    game = db.get_game(id)
    if game == None:
        return redirect(url_for('add_game'))
    player1 = game.game_players[0]
    player2 = game.game_players[1]
    return render_template( 'game_summary.html',
                            game_id=game.id,
                            player1=player1.name,
                            player2=player2.name,
                            rolls=game.game_roll)


if __name__ == '__main__':
    app.debug = True
    app.run()
