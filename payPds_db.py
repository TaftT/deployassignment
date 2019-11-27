import os
import psycopg2
import psycopg2.extras
import urllib.parse

# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

class payPdsDB:
    def __init__(self):

        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        # self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createPaypdTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS payPd (id SERIAL PRIMARY KEY, date VARCHAR(255), totalSavings INTEGER, difference INTEGER, differenceGoal INTEGER, accounts VARCHAR(255))")
        self.connection.commit()

    def insert(self, date ,totalSavings ,difference,differenceGoal, accounts):
        data = [date ,totalSavings ,difference,differenceGoal, accounts]
        self.cursor.execute("INSERT INTO payPds (date ,totalSavings,diff,diffGoal, account) VALUES (%s,%s,%s,%s,%s)",data)
        self.connection.commit()

    def getAllPayPds(self):
        self.cursor.execute("SELECT * FROM payPds")
        result = self.cursor.fetchall()
        return result

    def countAllPayPds(self):
        self.cursor.execute("SELECT COUNT(*) FROM payPds")
        result = self.cursor.fetchone()
        resp = result["COUNT(*)"]
        return resp

    def getListofIDs(self):
        ids=[]
        self.cursor.execute("SELECT id FROM payPds")
        result = self.cursor.fetchall()
        for item in result:
            ids.append(item["id"])
        return ids

    def getPayPd(self,id):
        id = [id]
        self.cursor.execute("SELECT * FROM payPds WHERE id = %s", id)
        result = self.cursor.fetchone()
        return result

    def getLastPayPd(self):
        listids = self.getListofIDs()
        id = [listids[self.countAllPayPds()-1]]
        self.cursor.execute("SELECT * FROM payPds WHERE id = %s", id)
        result = self.cursor.fetchone()
        return result

    def deletePayPd(self,id):
        result = self.getPayPd(id)
        id = [id]
        self.cursor.execute("DELETE FROM payPds WHERE id = %s", id)
        self.connection.commit()
        return result

    def updateOne(self, date ,totalSavings ,difference,differenceGoal, accounts, id):
        data = [date ,totalSavings ,difference,differenceGoal, accounts ,id]
        self.cursor.execute("UPDATE payPds SET date= %s, totalSavings= %s, diff= %s, diffGoal= %s, account= %s WHERE id=%s",data)
        self.connection.commit()

class usersDB:
    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        # self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createUserTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, fname VARCHAR(255), lname VARCHAR(255), email VARCHAR(255), hashpass VARCHAR(255))")
        self.connection.commit()

    def insertUser(self, fname , lname, email, hashpass):
        data = [fname, lname, email, hashpass]
        self.cursor.execute("INSERT INTO users (fname, lname, email, hashPass) VALUES (%s,%s,%s,%s)",data)
        self.connection.commit()

    def getAllUsers(self):
        self.cursor.execute("SELECT * FROM users")
        result = self.cursor.fetchall()
        return result

    def getUser(self,id):
        id = [id]
        self.cursor.execute("SELECT * FROM users WHERE id = %s", id)
        result = self.cursor.fetchone()
        return result

    def getUserbyemail(self,email):
        email = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = %s", email)
        result = self.cursor.fetchone()
        return result

    def deleteUser(self,id):
        id = [id]
        self.cursor.execute("SELECT * FROM users WHERE id = %s", id)
        result = self.cursor.fetchone()
        self.cursor.execute("DELETE FROM users WHERE id = %s", id)
        self.connection.commit()
        return result

    def updateOneUser(self, fname , lname, email, hashpass, id):
        data = [fname, lname, email, hashpass, id]
        self.cursor.execute("UPDATE users SET fname= %s, lname= %s, email= %s, hashPass= %s WHERE id=%s",data)
        self.connection.commit()
