from utils import dict_to_board


class User:

    def __init__(self, user_id, email, name):
        self.user_id = user_id
        self.email = email
        self.name = name

    def serialize(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
        }


class Game:

    def __init__(self, game_id, player1, player2):
        self.game_id = game_id
        self.player1 = player1
        self.player2 = player2
        self.boards = {player1['user_id']: [[]], player2['user_id']: [[]]}
        self.players_joined = {player1['user_id']: False, player2['user_id']: False}
        self.current_player = player1

    def set_board(self, user_id, cells):
        board = dict_to_board(cells)
        self.boards.update({user_id: board})

    def join_player(self, user_id):
        self.players_joined.update({user_id: True})

    def both_players_joined(self):
        return all(self.players_joined.values())

    def boards_ready(self):
        return all(self.boards.values())

    def shoot(self, user_id, json_board):
        pass

    def winner(self):
        return


class Cell:

    boat = False

    def __init__(self, boat):
        self.boat = boat

    def __str__(self):
        return self.boat

    def toJSON(self):
        return {"boat": self.boat}
