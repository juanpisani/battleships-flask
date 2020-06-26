import numpy as np

from exceptions.game_exception import GameException
from utils import dict_to_board, empty_boat_board, empty_shot_board


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
        self.boat_boards = {player1['user_id']: empty_boat_board(), player2['user_id']: empty_boat_board()}
        self.players_boards_ready = {player1['user_id']: False, player2['user_id']: False}
        self.shot_boards = {player1['user_id']: empty_shot_board(), player2['user_id']: empty_shot_board()}
        self.players_joined = {player1['user_id']: False, player2['user_id']: False}
        self.current_player = player1
        self.hits = {player1['user_id']: 0, player2['user_id']: 0}

    def set_board(self, user_id, cells):
        board = dict_to_board(cells)
        self.boat_boards.update({user_id: board})
        self.players_boards_ready.update({user_id: True})

    def join_player(self, user_id):
        self.players_joined.update({user_id: True})

    def both_players_joined(self):
        return all(self.players_joined.values())

    def boards_ready(self):
        return all(self.players_boards_ready.values())

    # return hit, sunken, game_ended, changed_turn
    def shoot(self, x, y, user_id):
        opponent_id = self.player1['user_id']
        if user_id == opponent_id:
            opponent_id = self.player2['user_id']
        opponent_board = self.boat_boards[opponent_id]
        self.shot_boards[user_id][y][x].shot = True
        if not opponent_board[y][x].boat:
            self.missed_shot(x, y, user_id, opponent_id)
            self.change_turn()
            return False, False, False, True
        self.hit_shot(x, y, user_id, opponent_id)
        return True, self.last_part_of_boat(x, y), self.check_end_game(user_id), False

    def missed_shot(self, x, y, user_id, opponent_id):
        self.shot_boards[user_id][y][x].hit = False
        self.boat_boards[opponent_id][y][x].hit = False

    def hit_shot(self, x, y, user_id, opponent_id):
        self.shot_boards[user_id][y][x].hit = True
        self.boat_boards[opponent_id][y][x].hit = True
        self.hits[user_id] += 1

    def validate_shot(self, user_id, x, y):
        if self.shot_boards[user_id][y][x].shot:
            raise GameException('invalid_shot', 'Already made a shot there')

    # TODO PARA VER SI FUE HUNDIDO
    def last_part_of_boat(self, x, y):
        return False

    # TODO CUANTOS HITS TIENE Q TENER PARA GANAR?
    def check_end_game(self, user_id):
        return self.hits[user_id] == 20

    def change_turn(self):
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def winner(self):
        return


class BoatCell:

    def __init__(self, boat, hit):
        self.boat = boat
        self.hit = hit

    def toJSON(self):
        return {"boat": self.boat}


class ShotCell:

    def __init__(self, shot, hit):
        self.shot = shot
        self.hit = hit

    def toJSON(self):
        return {"shot": self.shot}

