import numpy as np

from exceptions.game_exception import GameException
from models import models
from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

SHIPS_AMOUNT = {
    'one_pieces': 4,
    'two_pieces': 3,
    'three_pieces': 2,
    'four_pieces': 1
}

# ROW_MAP = {
#     'A': 0,
#     'B': 1,
#     'C': 2,
#     'D': 3,
#     'E': 4,
#     'F': 5,
#     'G': 6,
#     'H': 7,
#     'I': 8,
#     'J': 9,
#     0: 'A',
#     1: 'B',
#     2: 'C',
#     3: 'D',
#     4: 'E',
#     5: 'F',
#     6: 'G',
#     7: 'H',
#     8: 'I',
#     9: 'J',
# }


# also validates board setup
# fila x columna
def dict_to_board(board):
    one_piece_boats = 0
    two_piece_boats = 0
    three_piece_boats = 0
    four_piece_boats = 0

    piece_count = 0

    result = np.empty((10, 10), dtype=models.BoatCell)
    for i in range(len(board)):
        if piece_count == 2:
            two_piece_boats += 1
        elif piece_count == 3:
            three_piece_boats += 1
        elif piece_count == 4:
            four_piece_boats += 1
        piece_count = 0
        extreme1 = board[i]['extreme1']
        extreme2 = board[i]['extreme2']
        lower = extreme1
        higher = extreme2
        # caso {extreme1: A1, extreme2: A1}
        if extreme1 == extreme2:
            result[int(extreme1[1])][int(extreme1[0])] = models.BoatCell(True, False)
            one_piece_boats += 1
        # caso {extreme1: A1, extreme2: A4}
        elif int(extreme1[0]) == int(extreme2[0]):
            if int(extreme1[1]) > int(extreme2[1]):
                lower = int(extreme2)
                higher = int(extreme1)
            for j in range(int(lower[1]), int(higher[1]) + 1):
                result[j][int(lower[0])] = models.BoatCell(True, False)
                piece_count += 1
        else:
            # caso {extreme1: C5, extreme2: F5}
            if int(extreme1[0]) > int(extreme2[0]):
                lower = int(extreme2)
                higher = int(extreme1)
            for j in range(int(lower[0]), int(higher[0]) + 1):
                result[int(lower[1])][j] = models.BoatCell(True, False)
                piece_count += 1
    if piece_count == 2:
        two_piece_boats += 1
    elif piece_count == 3:
        three_piece_boats += 1
    elif piece_count == 4:
        four_piece_boats += 1
    for i in range(0, 10):
        for j in range(0, 10):
            if result[i][j] is None:
                result[i][j] = models.BoatCell(False, False)
    validate_boat_count(dict(one=one_piece_boats, two=two_piece_boats, three=three_piece_boats, four=four_piece_boats))
    return result


def validate_boat_count(count_dict):
    if count_dict['one'] == SHIPS_AMOUNT['one_pieces'] and count_dict['two'] == SHIPS_AMOUNT['two_pieces'] and \
            count_dict['three'] == SHIPS_AMOUNT['three_pieces'] and count_dict['four'] == SHIPS_AMOUNT['four_pieces']:
        return
    raise GameException('setup_boards', 'Invalid boat setup')


def empty_shot_board():
    result = np.empty((10, 10), dtype=models.ShotCell)
    for i in range(0, 10):
        for j in range(0, 10):
            if result[i][j] is None:
                result[i][j] = models.ShotCell(False, False)
    return result


def empty_boat_board():
    result = np.empty((10, 10), dtype=models.BoatCell)
    for i in range(0, 10):
        for j in range(0, 10):
            if result[i][j] is None:
                result[i][j] = models.BoatCell(False, False)
    return result
