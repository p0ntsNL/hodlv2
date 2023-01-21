# pylint: disable-all
import hashlib
import json

import yaml
from bson import ObjectId, json_util
from flask import request, session
from run import app, db


def getHashed(text):
    salt = "7be8c273dc1f90da9e765526"
    hashed = text + salt
    hashed = hashlib.md5(hashed.encode())
    hashed = hashed.hexdigest()
    return


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
    return list(data), len(list(data))


def mongodb_count_documents(collection, criteria):
    return db[collection].count_documents(criteria)


def get_active_trades():
    active_trades = db.trades.find({"status": "active"}).sort("open.info.opentm", 1)
    trades = []
    for t in active_trades:
        get_last = db.markets.find_one({"_id": t["market"]})
        t["last"] = get_last["last"]
        trades.append(t)
    return trades, len(trades)


def get_finished_trades():
    finished_trades = db.trades.find({"status": "finished"}).sort(
        "close.info.closetm", -1
    )
    trades = []
    for t in finished_trades:
        trades.append(t)
    return trades, len(trades)


def get_profits():
    return db.trades.aggregate(
        [
            {"$sort": {"profit_currency": 1}},
            {"$match": {"status": "finished"}},
            {"$group": {"_id": "$profit_currency", "sum_val": {"$sum": "$profit"}}},
        ]
    )


def get_logging():
    return db.logs.find().sort("timestamp", 1)


def get_configuration():
    data = db.configuration.find_one({"_id": "configuration"})
    del data["_id"]
    data["ExchangeSettings"]["ExchangeSecret"] = "***"
    data["ExchangeSettings"]["ExchangePassword"] = "***"
    data["PushoverSettings"]["PushoverAppToken"] = "***"
    return data
