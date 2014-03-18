import os
import shelve

from flask import Flask, render_template, request, url_for, redirect
from flask.ext.zodb import ZODB, List
from model import Game
from parser import LogFileParser


UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = set( ['png'])

app    = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
here = os.path.dirname(__file__)
static_dir = os.path.join( here, app.config['UPLOAD_FOLDER'] )
shelve_storage_path = os.path.join(static_dir, 'shelve.db')
db = shelve.open(  shelve_storage_path )

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
    for guid in db.keys():
        game = db[guid]
        url_text = "{0} vs {1} ({2})".format(game.player1, game.player2, game.game_date)
        ret.append( { 'text' : url_text, 'guid' : 'game?id=' + guid})
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


    game = Game(static_dir)
    game.run_the_tape(tape, winner, LogFileParser() )


    game.create_and_stash_graphs()
    db[game.game_id] = game
    return redirect( url_for('game', id=str(game.game_id)) )

    #except Exception as inst:
     #   print (inst)
      #  error_dir = os.path.join( static_dir, "bad_chat_logs")
       # error_file = os.path.join( error_dir, str(uuid.uuid4() ) + ".txt" )
        #fd = open( error_file, 'w' )
        #fd.write( tape.encode('ascii', 'ignore') )
        #fd.close()
        #return render_template( 'game_error.html' )


@app.route('/game')
def game():
    uuid = str(request.args.get('id'))
    game = db[uuid]
    if game == None:
        return redirect(url_for('add_game'))
    return render_template( 'result.html',
                             imagesrc=game.get_graph_image(),
                             p1stat=game.player1_dice_stats(),
                             p2stat=game.player1_dice_stats(),
                             player1=game.player1,
                             player2=game.player2,
                             winner=game.winner)


if __name__ == '__main__':
    app.debug = True
    app.run()
