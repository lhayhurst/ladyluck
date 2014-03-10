import os
import pickle
import uuid
import time
from flask import Flask, render_template, request, url_for, redirect, make_response, flash
import shutil
from werkzeug.utils import secure_filename
from lgraph import LuckGraphs
from parser import LogFileParser
from stats import DiceStats


UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = set( ['png'])

app    = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
here = os.path.dirname(__file__)
static_dir = os.path.join( here, app.config['UPLOAD_FOLDER'] )


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
    for file in os.listdir( static_dir ):
        prefix_suffix = os.path.splitext(file)
        if prefix_suffix[1] == ".pik":
            summary_stats = pickle.load( open( os.path.join(static_dir, file ), 'r' ) )
            url_text = "{0} vs {1} ({2})".format(summary_stats[0].player, summary_stats[1].player, summary_stats[2])
            guid     = prefix_suffix[0]
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
    input  = request.form['chatlog']
    winner = request.form['winner']
    if len(input) == 0:
        return redirect(url_for('new'))
    parser = LogFileParser()

    try:
        parser.read_input_from_string(input)
        parser.run_finite_state_machine()
        graphs = LuckGraphs(parser.turns)

        #build the stats graphs
        output = graphs.get_output()
        output.seek(0)
        game_uuid = uuid.uuid4()
        filename = secure_filename( str(game_uuid) + '.png')
        full_pwd = os.path.join( static_dir, filename)
        fd = open( full_pwd, 'w')
        shutil.copyfileobj( output, fd )

        pickled_game_name = secure_filename(str(game_uuid) + '.pik' )
        full_pickle_path  = os.path.join( static_dir, pickled_game_name)
        pickle.dump( parser, open(full_pickle_path, 'wb') )

        #build the summary stats
        summary_stats = get_summary_stats(parser.turns, winner)
        pickled_game_name = secure_filename(str(game_uuid) + '.pik' )
        full_pickle_path  = os.path.join( static_dir, pickled_game_name)
        pickle.dump( summary_stats, open(full_pickle_path, 'wb') )
    except Exception as inst:
        error_dir = os.path.join( static_dir, "bad_chat_logs")
        error_file = os.path.join( error_dir, str(uuid.uuid4() ) + ".txt" )
        fd = open( error_file, 'w' )
        fd.write( input )
        fd.close()
        return render_template( 'game_error.html' )

    return redirect( url_for('game', id=str(game_uuid)) )

@app.route('/game')
def game():
    uuid = request.args.get('id')
    pickled_game_name = secure_filename(str(uuid) + '.pik' )
    full_pickle_path  = os.path.join( static_dir, pickled_game_name)
    if not os.path.exists( full_pickle_path ):
        #TODO: redirect them to a more useful page
        return redirect(url_for('add_game'))
    summary_stats = pickle.load( open(full_pickle_path, 'r') )
    filename = secure_filename( uuid + '.png')
    winner = None
    if len(summary_stats) == 3: #backwards compat hack
        winner = "Unknown"
    else:
        winner = summary_stats[3]
        if winner == None or len(winner) == 0:
           winner = "Unknown"
    return render_template( 'result.html',
                             imagesrc=filename,
                             results=(summary_stats[0],summary_stats[1]),
                             player1=summary_stats[0].player,
                             player2=summary_stats[1].player,
                             winner=winner)

def get_summary_stats(turns, winner):

    player1_stats = None
    player2_stats = None
    player1       = None
    player2       = None

    ret = []
    for turn in turns:
        if player1 == None:
            player1 = turn.attacking_player
            player1_stats = DiceStats(player1)
        if player1 != None and player2 == None:
            player2 = turn.attacking_player
            player2_stats = DiceStats(player2)

    for turn in turns:
        for roll in turn.attack_rolls:
            if roll.player == player1:
                player1_stats.add_roll(roll, 'Attack')
            else:
                player2_stats.player = roll.player
                player2_stats.add_roll(roll, 'Attack')

        for roll in turn.defense_rolls:
            if roll.player == player1:
                player1_stats.add_roll(roll, 'Defend')
            else:
                player2_stats.add_roll(roll, 'Defend')

    ret.append(player1_stats)
    ret.append(player2_stats)
    ret.append(time.strftime("%m-%d-%Y"))
    ret.append(winner)
    return ret



if __name__ == '__main__':
    app.debug = True
    app.run()
