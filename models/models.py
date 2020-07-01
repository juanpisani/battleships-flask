import random

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

    def __init__(self, game_id, player1):
        self.game_id = game_id
        self.player1 = player1
        self.player2 = None
        self.boat_boards = None
        self.players_boards_ready = None
        self.shot_boards = None
        self.players_joined = None
        self.current_player = player1
        self.hits = None
        self.players_rematch = None

    def receive_second_player(self, player2):
        self.player2 = player2
        self.boat_boards = {self.player1['user_id']: empty_boat_board(), player2['user_id']: empty_boat_board()}
        self.players_boards_ready = {self.player1['user_id']: False, player2['user_id']: False}
        self.shot_boards = {self.player1['user_id']: empty_shot_board(), player2['user_id']: empty_shot_board()}
        self.players_joined = {self.player1['user_id']: False, player2['user_id']: False}
        self.hits = {self.player1['user_id']: 0, player2['user_id']: 0}
        self.players_rematch = {self.player1['user_id']: False, player2['user_id']: False}

    def set_board(self, user_id, cells):
        # dict_to_board also validates board setup
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
        self.shot_boards[user_id][x][y].shot = True
        if not opponent_board[x][y].boat:
            self.missed_shot(x, y, user_id, opponent_id)
            self.change_turn()
            return False, False, False, True
        self.hit_shot(x, y, user_id, opponent_id)
        return True, self.last_part_of_boat(x, y, opponent_board), self.check_end_game(user_id), False

    def missed_shot(self, x, y, user_id, opponent_id):
        self.shot_boards[user_id][x][y].hit = False
        self.boat_boards[opponent_id][x][y].hit = False

    def hit_shot(self, x, y, user_id, opponent_id):
        self.shot_boards[user_id][x][y].hit = True
        self.boat_boards[opponent_id][x][y].hit = True
        self.hits[user_id] += 1

    def validate_shot(self, user_id, x, y):
        if self.shot_boards[user_id][x][y].shot:
            raise GameException('invalid_shot', 'Already made a shot there')

    def last_part_of_boat(self, x, y, board):
        return self.check_left(x-1, y, board) \
               and self.check_right(x+1, y, board) \
               and self.check_down(x, y-1, board) \
               and self.check_up(x, y+1, board)

    def check_left(self, x, y, board):
        try:
            if board[x][y].boat:
                if board[x][y].hit:
                    return self.check_left(x - 1, y, board)
                else:
                    return False
            else:
                return True
        except IndexError:
            return True

    def check_right(self, x, y, board):
        try:
            if board[x][y].boat:
                if board[x][y].hit:
                    return self.check_right(x + 1, y, board)
                else:
                    return False
            else:
                return True
        except IndexError:
            return True

    def check_up(self, x, y, board):
        try:
            if board[x][y].boat:
                if board[x][y].hit:
                    return self.check_up(x, y + 1, board)
                else:
                    return False
            else:
                return True
        except IndexError:
            return True

    def check_down(self, x, y, board):
        try:
            if board[x][y].boat:
                if board[x][y].hit:
                    return self.check_down(x, y - 1, board)
                else:
                    return False
            else:
                return True
        except IndexError:
            return True

    def check_end_game(self, user_id):
        return self.hits[user_id] == 20

    def change_turn(self):
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def random_shot(self, user_id):
        random_x = random.randint(0, 9)
        random_y = random.randint(0, 9)
        while self.shot_boards[user_id][random_x][random_y].shot:
            random_x = random.randint(0, 9)
            random_y = random.randint(0, 9)
        return random_x, random_y

    # returns if both want rematch
    def player_wants_rematch(self, user_id):
        self.players_rematch.update({user_id: True})
        return all(self.players_rematch.values())

    def clear(self):
        self.boat_boards = {self.player1['user_id']: empty_boat_board(), self.player2['user_id']: empty_boat_board()}
        self.players_boards_ready = {self.player1['user_id']: False, self.player2['user_id']: False}
        self.shot_boards = {self.player1['user_id']: empty_shot_board(), self.player2['user_id']: empty_shot_board()}
        self.hits = {self.player1['user_id']: 0, self.player2['user_id']: 0}
        self.players_rematch = {self.player1['user_id']: False, self.player2['user_id']: False}
        self.current_player = self.player1


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

