#!/usr/bin/env python3
# pylint: disable=import-error,wildcard-import,wrong-import-position
"""
Main worker class
"""

import pymongo
from flask import Flask

app = Flask(__name__)

from views import *  # isort:skip
from hodlv2.config import WEB_FLASK_SECRET  # isort:skip
from hodlv2.config import MONGODB_HOST, MONGODB_PORT, WEB_HOST, WEB_PORT  # isort:skip

client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client["hodlv2"]

if __name__ == "__main__":
    app.secret_key = WEB_FLASK_SECRET
    app.run(host=WEB_HOST, port=WEB_PORT)
