#!/usr/bin/env python3
# pylint: disable=import-error,wildcard-import,wrong-import-position
"""
Main worker class
"""

import pymongo
from flask import Flask

app = Flask(__name__)

from views import *

client = pymongo.MongoClient("127.0.0.1", 27017)
db = client["hodlv2"]

if __name__ == "__main__":
    app.secret_key = "d07651a4be534b30c6b844705020f1c5"
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)
