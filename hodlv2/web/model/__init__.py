import json

from app import app
from bson import ObjectId, json_util
from flask import request, session
from helpers.database import *
from helpers.hashpass import *


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


def finduser():
    find = db.users.find()
    if find:
        for u in find:
            if "username" in u:
                return True, u["username"]
    return False, "HODLv2"


def registerUser():
    fields = [k for k in request.form]
    values = [request.form[k] for k in request.form]
    data = dict(zip(fields, values))
    user_data = json.loads(json_util.dumps(data))
    user_data["password"] = getHashed(user_data["password"])
    user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
    db.users.insert_one(user_data)


def mongodb_find(collection, criteria):
    data = db[collection].find(criteria)
    return data, data.count()


def mongodb_count_documents(collection, criteria):
    return db[collection].count_documents(criteria)
