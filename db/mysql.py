from datetime import datetime

import pymysql


class Database:

    def __init__(self):
        host = "localhost"
        user = "root"
        password = "password"
        db = "battleships"
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()
        try:
            self.cur.execute("CREATE TABLE Game(winner_id varchar(100), loser_id varchar(100), date varchar(100))")
            self.cur.execute("CREATE TABLE User(user_id varchar(100), email varchar(100), name varchar(100))")
        except Exception:
            # table already exists
            pass

    def save_user(self, user):
        self.cur.execute("insert into User values('{0}', '{1}', '{2}')".format(user.user_id, user.email, user.name))
        return self.con.commit()

    def save_game(self, winner, loser):
        self.cur.execute("insert into Game values('{0}', '{1}', '{2}')".format(winner, loser, datetime.now()))
        return self.con.commit()

    def list_users(self):
        self.cur.execute("SELECT first_name, last_name, gender FROM USER")
        return self.cur.fetchall()

    def get_user_history(self, user_id):
        self.cur.execute('select * from Game where winner_id = ' + user_id + ' or loser_id = ' + user_id)
        history = self.cur.fetchall()
        return history

    def get_user_wins_stats(self, user_id):
        self.cur.execute('select count(*) from Game where winner_id = ' + user_id)
        wins = self.cur.fetchall()
        return wins[0]['count(*)']

    def get_user_loses_stats(self, user_id):
        self.cur.execute('select count(*) from Game where loser_id = ' + user_id)
        loses = self.cur.fetchall()
        return loses[0]['count(*)']

    def get_history_between_users(self, user_1, user_2):
        self.cur.execute('select count from Game where (winner_id = ' + user_1 + ' and loser_id = ' + user_2 + ') or (winner_id = ' + user_2 + ' and loser_id = ' + user_1 + ')')
        history = self.cur.fetchall()
        return history

    def get_user(self, user_id):
        self.cur.execute('select * from User where user_id = ' + user_id)
        users = self.cur.fetchall()
        return users[0] if users else None
