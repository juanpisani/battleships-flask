import json
import logging
import uuid

from flask_socketio import SocketIO, join_room
from flask import Flask, request

from flask_cors import cross_origin, CORS
from google.auth.transport import requests
from google.oauth2 import id_token

from db.mysql import Database
from exceptions.game_exception import GameException
from models.models import Game, User

app = Flask(__name__)
cors = CORS(app=app)

socketio = SocketIO(app, cors_allowed_origins="*")

GOOGLE_CLIENT_ID = '168742262050-ojjs8no69pmvclfjmc1h110drusu7gf7.apps.googleusercontent.com'

db = Database()

possible_opponents = []
games = []
user_game = {}


@app.route('/api/auth', methods=['POST'])
@cross_origin()
def register_google():
    token = request.json["id_token"]
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        user_id = id_info['sub']
        user = db.get_user(user_id)
        if user:
            logging.info(
                "User ${user_name} with ID ${id} is logged in".format(user_name=user['name'], id=user['user_id']))
            return json.dumps(user), 200
        else:
            new_user = User(id_info['sub'], id_info['email'], id_info['name'])
            db.save_user(new_user)
            logging.info(
                "User ${user_name} with ID ${id} is being registered".format(user_name=new_user.name,
                                                                             id=new_user.user_id))
            return json.dumps(new_user.serialize()), 201
    except ValueError:
        # Invalid token
        pass


@app.route('/api/history', methods=['POST'])
@cross_origin()
def get_user_history():
    user_id = request.json["user_id"]
    return json.dumps(db.get_user_history(user_id))


# TODO DISCONNECT
@socketio.on('connect_player')
def connect_player(json_obj):
    user = db.get_user(json_obj["user_id"])
    possible_opponents.append(user)
    if len(possible_opponents) == 1:
        game = create_game(possible_opponents[0])
        user_game[user['user_id']] = game.game_id
        join_room(game.game_id, request.sid)
        socketio.emit('connected_player', dict(player=user), room=game.game_id)
    if len(possible_opponents) == 2:
        if possible_opponents[0] == possible_opponents[1]:
            possible_opponents.pop(1)
            return
        game = get_game(user_game[possible_opponents[0]['user_id']])
        game.receive_second_player(possible_opponents[1])
        join_room(game.game_id, request.sid)
        user_game[user['user_id']] = game.game_id
        socketio.emit('connected_player', dict(player=user), room=game.game_id)
        socketio.emit('ready_to_start', dict(game=game.game_id, player_1=possible_opponents[0], player_2=possible_opponents[1]), room=game.game_id)
        possible_opponents.clear()


@socketio.on('join_room')
def join_game_room(json_obj):
    user = db.get_user(json_obj["user_id"])
    game = json_obj['game_id']
    join_room(game, request.sid)
    socketio.emit('room_update', {"message": "Welcome user " + str(user['user_id'])}, room=game)
    game_instance = get_game(game)
    game_instance.join_player(user['user_id'])
    if game_instance.both_players_joined():
        socketio.emit('ready_for_setup', {"message": "Start pieces setup"}, room=game)


@socketio.on('setup_board')
def board_ready(json_obj):
    game = get_game(json_obj['game_id'])
    user = db.get_user(json_obj['user_id'])
    game.set_board(user['user_id'], json_obj['board'])
    socketio.emit('user_board_received', dict(user_id=user['user_id']), room=game.game_id)
    if game.boards_ready():
        socketio.emit("boards_ready", dict(message='Boards are ready, start to play!'), rooom=game.game_id)
        socketio.emit("player_turn", dict(user_id=game.current_player['user_id']), room=game.game_id)


@socketio.on('fire')
def fire(json_obj):
    game = get_game(json_obj['game_id'])
    user = db.get_user(json_obj['user_id'])
    if user != game.current_player:
        raise GameException("user_shot", "Wrong turn")
    x = json_obj['x']
    y = json_obj['y']
    game.validate_shot(user['user_id'], x, y)
    hit, sunken, game_ended, turn_changed = game.shoot(x, y, user['user_id'])
    socketio.emit('shot_processed', dict(user_shot=json_obj['user_id'], hit=hit, sunken=sunken, x=x, y=y), room=game.game_id)
    if game_ended:
        socketio.emit('game_ended', dict(winner=user), room=game.game_id)
        user_game.pop(game.player1['user_id'])
        user_game.pop(game.player2['user_id'])
        games.remove(game)
        opponent = get_opponent(user['user_id'], game)
        db.save_game(user['user_id'], opponent['user_id'])
    elif turn_changed:
        socketio.emit("player_turn", dict(user_id=game.current_player['user_id']), room=game.game_id)


@socketio.on('left_room')
def leave_room(json_obj):
    game = get_game(json_obj['game_id'])
    if game is None:
        return
    user_id = json_obj['user_id']
    winner = get_opponent(user_id, game)
    socketio.emit('game_ended', dict(winner=winner), room=game.game_id, include_self=False)
    user_game.pop(game.player1['user_id'])
    user_game.pop(game.player2['user_id'])
    games.remove(game)
    db.save_game(winner['user_id'], user_id)


@socketio.on('random_shot')
def random_shot(json_obj):
    user_id = json_obj['user_id']
    game = get_game(json_obj['game_id'])
    x, y = game.random_shot(user_id)
    return fire(dict(user_id=user_id, game_id=game.game_id, x=x, y=y))


def create_game(player_1):
    game = Game(str(uuid.uuid1()), player_1)
    games.append(game)
    return game


def get_game(game_id):
    for game in games:
        if game.game_id == game_id:
            return game
#     TODO ERROR


def get_opponent(user_id, game):
    if game.player1['user_id'] == user_id:
        return game.player2
    return game.player1


if __name__ == '__main__':
    app.run()
