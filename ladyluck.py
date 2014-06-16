import os
import uuid
import MySQLdb

from flask import render_template, request, url_for, redirect, Response, make_response
import myapp

from game_summary_stats import GameTape
from parser import LogFileParser
from persistence import Game, PersistenceManager
from plots.player_plots import LuckPlot, VersusPlot, AdvantagePlot, DamagePlot

app =  myapp.create_app()
UPLOAD_FOLDER = "static"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = set( ['png'])



here = os.path.dirname(__file__)
static_dir = os.path.join( here, app.config['UPLOAD_FOLDER'] )

ADMINS = ['sozinsky@gmail.com']

session = myapp.db_connector.get_session()

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/games" )
def games():
    try:
        games = PersistenceManager(myapp.db_connector).get_games(myapp.db_connector.get_session())
        return( render_template('games.html', games=games) )
    except MySQLdb.dbOperationalError:
        #give it another shot...
        games = PersistenceManager(myapp.db_connector).get_games(myapp.db_connector.get_session())
        return( render_template('games.html', games=games) )

@app.route("/editgames")
def editgames():
    try:
        games = PersistenceManager(myapp.db_connector).get_games(myapp.db_connector.get_session())
        return( render_template('games-edit.html', games=games) )
    except MySQLdb.dbOperationalError:
        #give it another shot...
        games = PersistenceManager(myapp.db_connector).get_games(myapp.db_connector.get_session())
        return( render_template('games-edit.html', games=games) )


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

    try:
        parser = LogFileParser(session)
        parser.read_input_from_string(tape)
        parser.run_finite_state_machine()

        game = Game( session, parser.get_players())

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


        session.add(game)
        session.commit()

        return redirect( url_for('game', id=str(game.id) ) )

    except Exception as err:
        error_dir = os.path.join( static_dir, "bad_chat_logs")
        error_file = os.path.join( error_dir, str(uuid.uuid4() ) + ".txt" )
        fd = open( error_file, 'w' )
        fd.write( tape.encode('ascii', 'ignore') )
        fd.close()
        return render_template( 'game_error.html', errortext=str(err) )

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
    game = PersistenceManager(myapp.db_connector).get_game(session,game_id)
    def generate():
        rows = get_game_tape_text(game)
        for r in rows:
           yield ",".join(r) + '\n'

    disposition = "attachment; filename=game{0}_{1}_vs_{2}.csv".format(game.id_str(), game.game_players[0].name, game.game_players[1].name )
    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': disposition} )

@app.route('/delete_game')
def delete_game():
    id = str(request.args.get('id'))
    game = PersistenceManager(myapp.db_connector).get_game(session,id)
    if game == None:
        return redirect(url_for('new'))
    #doing this manually as I banged my head against the wall trying to get it to work using the sql alchemy cascade logic...
    for throw in game.game_throws:
        for result in throw.results:
            for adjustment in result.adjustments:
                myapp.db_connector.get_session().delete(adjustment)
            myapp.db_connector.get_session().delete(result)
        myapp.db_connector.get_session().delete(throw)
    myapp.db_connector.get_session().delete(game)
    myapp.db_connector.get_session().commit()

    return redirect(url_for('editgames'))




@app.route('/game')
def game():
    id = str(request.args.get('id'))
    game = PersistenceManager(myapp.db_connector).get_game(session,id)
    if game == None:
        return redirect(url_for('new'))

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

@app.route('/damage')
def damage():
    id = str(request.args.get('game_id'))
    game = PersistenceManager().get_game(session, id)

    if game.game_tape is None:
        game_tape = GameTape(game)
        game_tape.score()

    dp = DamagePlot( game )
    output = dp.plot()
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/advantage')
def advantage():
    id = str(request.args.get('game_id'))
    use_initial = int(request.args.get('initial'))
    game = PersistenceManager().get_game(session,id)

    ap = AdvantagePlot( game, use_initial )
    output = ap.plot()
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/versus')
def versus():
    id = str(request.args.get('game_id'))
    game = PersistenceManager().get_game(session,id)

    attacker_id = long(request.args.get('attacker'))
    defender_id = long(request.args.get('defender'))

    vp = VersusPlot( game, attacker_id, defender_id)
    output = vp.plot()
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/luck_graph')
def luck_graph():
    id = str(request.args.get('game_id'))
    game = PersistenceManager().get_game(session,id)

    player_id = long(request.args.get('player'))
    dice_type = request.args.get('dice_type')

    lp = LuckPlot( game, player_id, dice_type)
    return lp.plot()
    #response = make_response(output.getvalue())
    #response.mimetype = 'image/png'
    #return response


if __name__ == '__main__':
    app.debug = True
    app.run()
