import json
import logging

from flask_socketio import SocketIO
from flask import Flask, request

from flask_cors import cross_origin
from google.auth.transport import requests
from google.oauth2 import id_token

from db.mysql import Database
from models.models import User

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

GOOGLE_CLIENT_ID = '168742262050-ojjs8no69pmvclfjmc1h110drusu7gf7.apps.googleusercontent.com'

db = Database()

possible_opponents = []
rooms = []


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


@socketio.on('connect_player')
def connect_player(json_obj):
    user = db.get_user(json_obj["user_id"])
    possible_opponents.append(user)
    logging.info(
        "User {0} with ID {1} is in the lobby".format(user.name, user.user_id))
    logging.info(
        "Users in the lobby: {0}".format(str(possible_opponents)))
    if len(possible_opponents) == 1:
        socketio.emit('connected_player', dict(player=possible_opponents[0]), broadcast=True,
                      include_self=True)
    elif len(possible_opponents) == 2:
        socketio.emit('ready_to_start', dict(player_1=possible_opponents[0], player_2=possible_opponents[1]),
                      broadcast=True,
                      include_self=True)
    else:
        pass
        # TODO ERROR


if __name__ == '__main__':
    app.run()
