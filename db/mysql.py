import pymysql


class Database:

    def __init__(self):
        host = "localhost"
        user = "root"
        password = "Nueve12!"
        db = "battleships"
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()
        try:
            self.cur.execute("CREATE TABLE User(user_id varchar(100), email varchar(100), name varchar(100))")
        except Exception:
            # table already exists
            pass

    def save_user(self, user):
        self.cur.execute("insert into User values('{0}', '{1}', '{2}')".format(user.user_id, user.email, user.name))
        return self.con.commit()

    def list_users(self):
        self.cur.execute("SELECT first_name, last_name, gender FROM USER")
        return self.cur.fetchall()

    def get_user(self, user_id):
        self.cur.execute('select * from User where user_id = ' + user_id)
        users = self.cur.fetchall()
        return users[0] if users else None
