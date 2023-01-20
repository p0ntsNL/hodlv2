import hashlib

def getHashed(text):
    salt = "7be8c273dc1f90da9e765526"
    hashed = text + salt
    hashed = hashlib.md5(hashed.encode())
    hashed = hashed.hexdigest()
    return hashed
