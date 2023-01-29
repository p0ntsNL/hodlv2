#!/usr/bin/env python3
# pylint: disable=import-error,wildcard-import,wrong-import-position
"""
Main worker class
"""

import pymongo
from flask import Flask

app = Flask(__name__)

from views import *

from hodlv2.config import MONGODB_HOST, MONGODB_PORT, WEB_HOST, WEB_PORT

client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client["hodlv2"]

if __name__ == "__main__":
    app.secret_key = "d07651a4be534b30c6b844705020f1c5"
    app.run(host=WEB_HOST, port=WEB_PORT, debug=True, use_reloader=False)
