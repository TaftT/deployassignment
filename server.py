from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode
from payPds_db import payPdsDB, usersDB
from http import cookies
from passlib.hash import bcrypt
from sessionstore import SessionStore
import json
import datetime
import sys

sessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.sendcookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)


    def loadcookie(self):
        if  "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

    def sendcookie(self):
        for value in self.cookie.values():
            self.send_header("Set-Cookie", value.OutputString())


    def loadSession(self):
        self.loadcookie()
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value
            self.session = sessionStore.getSession(sessionId)
            if self.session == None:
                sessionId = sessionStore.createSession()
                self.session = sessionStore.getSession(sessionId)
                self.cookie["sessionId"] = sessionId
        else:
            sessionId = sessionStore.createSession()
            self.session = sessionStore.getSession(sessionId)
            self.cookie["sessionId"] = sessionId


    def do_OPTIONS(self):
        self.loadSession()
        self.send_response(200)

        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-type")
        self.end_headers()



    def do_GET(self):
        self.loadSession()
        if self.path == "/payPds":
            payPds = self.AllPayPdsRetrieve()
            self.sendBodytoClient(payPds)
        elif self.path.startswith("/payPd/"):
            payPd = self.OnePayPdRetrieve(id)
            self.sendBodytoClient(payPd)
        elif self.path == "/payPdIDs":
            body = {}
            self.sendBodytoClient(body)


        else:
            self.handle404()
        return

    def do_POST(self):
        self.loadSession()
        if self.path == "/payPds":
            self.payPDcreatecopy()
        elif self.path == "/ADDpayPds":
            self.payPdsCreateNew()
        elif self.path == "/users":
            self.CreateUser()
        elif self.path == "/session":
            self.CreateSession()
        else:
            self.handle404()
        return

    def do_DELETE(self):
        self.loadSession()
        if self.path.startswith("/payPd/"):
            self.OnePayPdDelete(id)
        elif self.path.startswith("/users/"):
            self.DeleteUser()
        return

    def do_PUT(self):
        self.loadSession()
        if self.path.startswith("/payPd/"):
            self.OnePayPdUpdate(id)
        elif self.path.startswith("/users/"):
            self.UpdateUser()
        return

    def encryptPass(self, password):
        hash = bcrypt.hash(password)
        return hash

    def verifyPass(self, password, hashpass):
        return bcrypt.verify(password,hashpass)

    def CreateSession(self):
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsedBody = parse_qs(body)
        email = parsedBody['email'][0]
        password  = parsedBody['password'][0]

        users = self.RetrieveAllusers()
        for user in users:
            if user["email"] == email:
                if self.verifyPass(password,user["hashpass"]):
                    self.session["userId"] = user['id']
                    self.handle201({"msg":"login success"})
                    return
                else:
                    self.handle401("login Failed")
                    return
        self.handle401("login Failed")
        return

    def RetrieveAllusers(self):
        myusers = usersDB()
        mylist = myusers.getAllUsers()
        return mylist

    def RetrieveUser(self):
        parts = self.path.split("/")
        id = parts[2]
        myusers = usersDB()
        user = myusers.getUser(id)
        return user

    def CreateUser(self):
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsedBody = parse_qs(body)
        if "password" not in parsedBody or "email" not in parsedBody:
            self.handle400("Please send info with valid key")
        else:
            myusers = usersDB()
            fname = parsedBody['fname'][0]
            lname = parsedBody['lname'][0]
            email = parsedBody['email'][0]
            password  = parsedBody['password'][0]
            hashedpassword = self.encryptPass(password)
            if self.checkemailexsists(email):
                self.handle422( "That email already exists!")
                return

            myusers.insertUser(fname,lname,email,hashedpassword)
            self.handle201({"msg" : "New user registered!"})

    def checkemailexsists(self,email):
        myusers = usersDB()
        if myusers.getUserbyemail(email) is None:
            return False
        else:
            return True



    def DeleteUser(self):
        parts = self.path.split("/")
        id = parts[2]
        myuser = usersDB()
        user = myuser.deleteUser(id)
        if user != None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")

            self.end_headers()

            body={'msg': "Deleted"}
            self.wfile.write(bytes(json.dumps(body), "utf-8"))
        else:
            self.handle404()

    def UpdateUser(self):
        pass

    def OnePayPdDelete(self,id):
        if "userId" not in self.session:
            self.handle401()
            return
        parts = self.path.split("/")
        id = parts[2]
        myPayPds = payPdsDB()
        payPd = myPayPds.deletePayPd(id)
        if payPd != None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")

            self.end_headers()

            body={'msg': "Deleted"}
            self.wfile.write(bytes(json.dumps(body), "utf-8"))
        else:
            self.handle404()


    def OnePayPdUpdate(self,id):
        if "userId" not in self.session:
            self.handle401()
            return
        parts = self.path.split("/")
        id = parts[2]
        myPayPds = payPdsDB()
        payPd = myPayPds.getPayPd(id)
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsedBody = parse_qs(body)
        if payPd != None:
            myPayPds = payPdsDB()
            allpayPds = self.AllPayPdsRetrieve()
            # if len(allpayPds)>0:
            #     copypayPd = allpayPds[len(allpayPds)-1]

            fulldate = str(datetime.datetime.now())
            datesplit = fulldate.split()
            date = datesplit[0]

            totalSavings  = self.getTotal(parsedBody['account'][0])
            diff  = self.getDiff(self.findPrevId(id),totalSavings)
            diffGoal  = 5639
            accounts  = parsedBody['account'][0]


            myPayPds.updateOne(date,totalSavings,diff,diffGoal,accounts, id)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")

            self.end_headers()

        else:
            self.handle404()

    def AllPayPdsRetrieve(self):
        if "userId" not in self.session:
            self.handle401()
            return
        myPayPds = payPdsDB()
        mylist = myPayPds.getAllPayPds()
        return mylist

    def OnePayPdRetrieve(self,id):
        if "userId" not in self.session:
            self.handle401({"error":"not authorized"})
            return
        parts = self.path.split("/")
        id = parts[2]
        myPayPds = payPdsDB()
        payPd = myPayPds.getPayPd(id)
        return payPd

    def payPDcreatecopy(self):
        if "userId" not in self.session:
            self.handle401()
            return
        myPayPds = payPdsDB()
        allpayPds = self.AllPayPdsRetrieve()
        copypayPd = allpayPds[len(allpayPds)-1]

        fulldate = str(datetime.datetime.now())
        datesplit = fulldate.split()
        date = datesplit[0]

        totalSavings  = self.getTotal(copypayPd["account"])
        diff  = self.getDiff(myPayPds.getLastPayPd()["id"],totalSavings)
        diffGoal  = copypayPd['diffGoal']
        accounts  = copypayPd['account']

        myPayPds.insert(date,totalSavings,diff,diffGoal,accounts)

        body = {"id" :  myPayPds.getLastPayPd()["id"],"allIDs":myPayPds.getListofIDs()}

        self.handle201(body)

    def payPdsCreateNew(self):
        if "userId" not in self.session:
            self.handle401()
            return
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsedBody = parse_qs(body)
        if "account" not in parsedBody:
            self.handle400("Please send info with valid key")
        else:
            myPayPds = payPdsDB()
            fulldate = str(datetime.datetime.now())
            datesplit = fulldate.split()
            date = datesplit[0]
            diffGoal  = 500
            account  = parsedBody['account'][0]
            totalSavings  = self.getTotal(account)
            if "diff" in parsedBody:
                diff = parsedBody['diff'][0]
            else:
                diff  = self.getDiff(self.findPrevId(id),totalSavings)

            myPayPds.insert(date,totalSavings,diff,diffGoal,account)

            resbody = {"id" :  myPayPds.getLastPayPd()["id"],"allIDs":myPayPds.getListofIDs()}
            self.handle201(resbody)

    def handle404(self):
        self.send_response(404)
        self.send_header("Content-Type", "application/json")

        self.end_headers()

        error={'error': "We couldn't find that path please enter another"}
        self.wfile.write(bytes(json.dumps(error), "utf-8"))

    def handle400(self,msg):
        self.send_response(400)

        self.end_headers()

        error={'error': msg}
        self.wfile.write(bytes(json.dumps(error), "utf-8"))

    def handle422(self,msg):
        print(msg)
        self.send_response(422)

        self.end_headers()

        error={'error': msg}
        self.wfile.write(bytes(json.dumps(error), "utf-8"))

    def handle401(self,body=None):
        print(body)
        self.send_response(401)

        self.end_headers()

        if body:
            self.wfile.write(bytes(json.dumps(body), "utf-8"))

    def handle201(self,body=None):
        self.send_response(201)
        self.send_header("Content-Type", "application/json")

        self.end_headers()

        if body:
            self.wfile.write(bytes(json.dumps(body), "utf-8"))



    def sendBodytoClient(self,body=None):
        if "userId" not in self.session:
            self.handle401({"error":"Please Log in or sign up."})
            return
        print("this is the body", body)
        if body != None and body != []:
            myPayPds = payPdsDB()
            try:
                body["allIDs"] = myPayPds.getListofIDs()
            except:
                body.append(myPayPds.getListofIDs())
            self.send_response(200)
            self.send_header("Content-Type", "application/json")

            self.end_headers()

            self.wfile.write(bytes(json.dumps(body), "utf-8"))
        else:
            self.handle404()

    def getTotal(self,accounts):
        lstaccounts = json.loads(accounts)
        total=0
        for account in lstaccounts:
            total+=float(account['amount'])
        return total

    def findPrevId(self, id):
        myPayPds = payPdsDB()
        ids = myPayPds.getListofIDs()
        print("this is the id ", id)
        print("this is the id list", ids[0])
        if len(ids)>1:
            for i in range(len(ids)):
                if int(ids[i])==int(id):
                    prevID=ids[i-1]
                    prev = myPayPds.getPayPd(ids[i-1])
                    if prev == None:
                        return 0
                    else:
                        return prevID
        else:
            return 0

    def getDiff(self,otherId,thistotalSavings):
        myPayPds = payPdsDB()
        if otherId<=0:
            prevPayPd = 0
        else:
            prevPayPdobj = myPayPds.getPayPd(otherId)
            prevPayPd = prevPayPdobj["totalsavings"]
        return thistotalSavings - prevPayPd




def run():
    db = payPdsDB()
    db.createPaypdTable()
    db = None # disconnect

    db = usersDB()
    db.createUserTable()
    db = None # disconnect

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)
    print("Listening...")
    server.serve_forever()

run()
