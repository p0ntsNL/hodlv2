# pylint: disable-all
import sys
import os
import bcrypt
import yaml
from flask import request, session
from run import app, db


def getHashed(pwd):
    pwd = pwd.encode('utf-8')
    mySalt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(pwd, mySalt)
    return pwd_hash


def checkloginusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "User does not exist."
    else:
        return "User exists."


def checkloginpassword():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    password = request.form["password"]
    password = password.encode('utf-8')
    if bcrypt.checkpw(password, check["password"]):
        session["username"] = username
        return "ok"
    else:
        return "notok"


def registerUser():
    user_data = request.form.to_dict()
    user_data["password"] = getHashed(user_data["password"])
    user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
    db.users.insert_one(user_data)


def finduser():

    try:
        find = db.users.find()
        if find:
            for u in find:
                if "username" in u:
                    return True, u["username"]
    except Exception as error:
        pass

    return False, "HODLv2"


def checkconfig():

    try:
        config = db.configuration.find_one({"_id":"configuration"})
        data = request.form.to_dict()

        # Remove ExchangeSecret from data if it is empty
        if not data["ExchangeSecret"]:
            del data["ExchangeSecret"]

        # Remove ExchangePassword from data if it is empty
        if not data["ExchangePassword"]:
            del data["ExchangePassword"]

        # Loop through form fields
        bot_sync = {}
        bot_markets = []
        for k,v in data.items():

            if k.startswith('Exchange'):
                config["ExchangeSettings"][k] = v
            if k.startswith('MongoDb'):
                config["MongoDbSettings"][k] = v
            if k.startswith('Logging'):
                config["LoggingSettings"][k] = v
            if k.startswith('Pushover'):
                config["PushoverSettings"][k] = v

            if k.startswith('Bot'):
                bot_id = k.split('_')[1]
                bot_k = k.split('_')[2]
                bot_v = v

                if bot_k == 'Market':
                    bot_sync[bot_id] = bot_v
                    bot_markets.append(bot_v)

        # Create BotSettings
        for k,v in data.items():

            if k.startswith('Bot'):
                bot_id = k.split('_')[1]
                bot_k = k.split('_')[2]
                bot_v = v
                bot_market = bot_sync[bot_id]

                # Force int
                if bot_k in [ "MaxTrades", "ResetNextTradePrice" ]:
                    bot_v = int(bot_v)

                # Force float
                if bot_k in [ "TradeValue", "PercOpen", "PercClose" ]:
                    bot_v = float(bot_v)

                if bot_market not in config["BotSettings"]:
                    config["BotSettings"][bot_market] = {}
                config["BotSettings"][bot_market][bot_k] = bot_v

        # Remove deleted markets
        active_markets = []
        for k,v in config["BotSettings"].items():
            active_markets.append(k)
        for k in active_markets:
            if k not in bot_markets:
                del config["BotSettings"][k]

        # Remove MongoDb Host and Port if others exist
        if "Host" in config["MongoDbSettings"] and "MongoDbHost" in config["MongoDbSettings"]:
            del config["MongoDbSettings"]["Host"]
        if "Port" in config["MongoDbSettings"] and "MongoDbPort" in config["MongoDbSettings"]:
            del config["MongoDbSettings"]["Port"]

        db.configuration.update_one({"_id": "configuration"}, {"$set":config})
        return "ok"
    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print (error)
        return f"Unable to verify configuration: {error}"


def get_active_trades():

    try:
        active_trades = db.trades.find({"status": "active"}).sort("open.info.opentm", 1)
        trades = []
        for t in active_trades:
            get_last = db.markets.find_one({"_id": t["market"]})
            t["last"] = get_last["last"]
            trades.append(t)
        return trades, len(trades)
    except Exception as error:
        return [], 0


def get_finished_trades():

    try:
        finished_trades = db.trades.find({"status": "finished"}).sort(
            "close.info.closetm", -1
        )
        trades = []
        for t in finished_trades:
            trades.append(t)
        return trades, len(trades)
    except Exception as error:
        return [], 0


def get_profits():

    try:
        profit_aggregates = db.trades.aggregate(
            [
                {"$sort": {"profit_currency": 1}},
                {"$match": {"status": "finished"}},
                {"$group": {"_id": "$profit_currency", "sum_val": {"$sum": "$profit"}}},
            ]
        )
        profit_perc_aggregates = db.trades.aggregate(
            [
                {"$sort": {"profit_currency": 1}},
                {"$match": {"status": "finished"}},
                {
                    "$group": {
                        "_id": "$profit_currency",
                        "sum_val": {"$sum": "$profit_perc"},
                    }
                },
            ]
        )
        profit_perc = 0
        for aggregate in profit_perc_aggregates:
            profit_perc += float(aggregate["sum_val"])

        return profit_aggregates, profit_perc
    except Exception as error:
        return [], 0


def get_logging():

    try:
        return db.logs.find().sort("timestamp", 1)
    except Exception as error:
        return []


def get_configuration():

    try:
        data = db.configuration.find_one({"_id": "configuration"})
        del data["_id"]
        data["ExchangeSettings"]["ExchangeSecret"] = ""
        data["ExchangeSettings"]["ExchangePassword"] = ""
        return data
    except Exception as error:
        return 'Unable to retrieve configuration from database.'
