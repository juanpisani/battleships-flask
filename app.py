import json
import logging
import uuid

from flask_socketio import SocketIO, join_room
from flask import Flask, request

from flask_cors import cross_origin, CORS
from google.auth.transport import requests
from google.oauth2 import id_token

from db.mysql import Database
from models.models import User, Game

app = Flask(__name__)
cors = CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

GOOGLE_CLIENT_ID = '168742262050-ojjs8no69pmvclfjmc1h110drusu7gf7.apps.googleusercontent.com'

db = Database()

possible_opponents = []
games = []


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


# TODO DISCONNECT
@socketio.on('connect_player')
def connect_player(json_obj):
    user = db.get_user(json_obj["user_id"])
    possible_opponents.append(user)
    socketio.emit('connected_player', dict(player=user), broadcast=True,
                  include_self=True)
    logging.info(
        "User {0} with ID {1} is in the lobby".format(user['name'], user['user_id']))
    logging.info(
        "Users in the lobby: {0}".format(str(possible_opponents)))
    if len(possible_opponents) == 2:
        game = create_game(possible_opponents[0], possible_opponents[1])
        socketio.emit('ready_to_start', dict(game=game.game_id, player_1=possible_opponents[0], player_2=possible_opponents[1]),
                      broadcast=True,
                      include_self=True)
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
    game.set_board(user.user_id, json_obj['board'])
    socketio.emit('user_state_update', {"user_id": user.id, "ready": True}, room=game.game_id, include_self=False)
    if game.boards_ready():
        socketio.emit("boards_ready", rooom=game.game_id, include_self=False)


@socketio.on('fire')
def fire(json_obj):
    game = get_game(json_obj['game_id'])
    user = db.get_user(json_obj['user_id'])
    if user != game.current_player:
        # TODO ERROR
        raise Exception("wrong turn")
    x = json_obj['x']
    y = json_obj['y']
    turn, winner = game.shoot(x, y, user.user_id)
    if winner:
        pass
    else:
        pass


def create_game(player_1, player_2):
    game = Game(str(uuid.uuid1()), player_1, player_2)
    games.append(game)
    return game


def get_game(game_id):
    for game in games:
        if game.game_id == game_id:
            return game
#     TODO ERROR


if __name__ == '__main__':
    app.run()
