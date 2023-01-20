from app import app
from flask import request, session
from helpers.database import *
from helpers.hashpass import *
from bson import json_util, ObjectId
import json

def checkloginusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "No User"
    else:
        return "User exists"

def checkloginpassword():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    password = request.form["password"]
    hashpassword = getHashed(password)
    if hashpassword == check["password"]:
        session["username"] = username
        return "correct"
    else:
        return "wrong"

def find_trades(criteria):
    trades = db.trades.find(criteria)
    return trades.count(), trades

def finduser():
    find = db.users.find()
    if find:
        for u in find:
            if 'username' in u:
                return True, u['username']
    return False, 'HODLv2'

def registerUser():
    fields = [k for k in request.form]                                      
    values = [request.form[k] for k in request.form]
    data = dict(zip(fields, values))
    user_data = json.loads(json_util.dumps(data))
    user_data["password"] = getHashed(user_data["password"])
    user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
    db.users.insert(user_data)

def count_documents(collection, criteria):
    return db[collection].count_documents(criteria)

