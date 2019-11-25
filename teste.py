from passlib.hash import bcrypt

# if self.path == "/hello":
#     self.send_responce(200)
#     self.send_header("Set-Cookie", "type=ChocolaTeChip")
#     self.send_header("Set-Cookie", "size=VeryHuge")
#     self.end_headers()
#
# return

def encryptPass(password):
    hash = bcrypt.hash(password)
    return hash

def verifyPass(password,hashpass):
    return bcrypt.verify(password,hashpass)

def main():
    saved = encryptPass("coolPass32")
    print(saved)
    wrong = "notpass89"
    print("wrong", verifyPass(wrong,saved))
    print("right", verifyPass("coolPass32",saved))
main()
