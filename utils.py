import numpy as np

from models import models

ROW_MAP = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7,
    'I': 8,
    'J': 9,
    0: 'A',
    1: 'B',
    2: 'C',
    3: 'D',
    4: 'E',
    5: 'F',
    6: 'G',
    7: 'H',
    8: 'I',
    9: 'J',
}


# fila x columna
def dict_to_board(board):
    result = np.empty((10, 10), dtype=models.BoatCell)
    for i in range(len(board)):
        extreme1 = board[i]['extreme1']
        extreme2 = board[i]['extreme2']
        lower = extreme1
        higher = extreme2
        # caso {extreme1: A1, extreme2: A1}
        if extreme1 == extreme2:
            result[ROW_MAP[extreme1[0]]][int(extreme1[1:]) - 1] = models.BoatCell(True).toJSON()
        # caso {extreme1: A1, extreme2: A4}
        elif extreme1[0] == extreme2[0]:
            if extreme1[1:] > extreme2[1:]:
                lower = extreme2
                higher = extreme1
            for j in range(int(lower[1:]) - 1, int(higher[1:])):
                result[ROW_MAP[lower[0]]][j] = models.BoatCell(True).toJSON()
        else:
            # caso {extreme1: C5, extreme2: F5}
            if ROW_MAP[extreme1[0]] > ROW_MAP[extreme2[0]]:
                lower = extreme2
                higher = extreme1
            for j in range(ROW_MAP[lower[0]], ROW_MAP[higher[0]] + 1):
                result[j][int(lower[1:]) - 1] = models.BoatCell(True).toJSON()
    for i in range(0, 10):
        for j in range(0, 10):
            if result[i][j] is None:
                result[i][j] = models.BoatCell(False).toJSON()
    return result


def empty_shot_board():
    result = np.empty((10, 10), dtype=models.ShotCell)
    for i in range(0, 10):
        for j in range(0, 10):
            if result[i][j] is None:
                result[i][j] = models.ShotCell(False).toJSON()
    return result


def empty_boat_board():
    result = np.empty((10, 10), dtype=models.BoatCell)
    for i in range(0, 10):
        for j in range(0, 10):
            if result[i][j] is None:
                result[i][j] = models.BoatCell(False).toJSON()
    return result
