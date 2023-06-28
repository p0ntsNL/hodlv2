#!/usr/bin/env python3
# pylint: disable=broad-except
"""
HODLv2 main script
"""

import logging
import sys
from logging import handlers

from log4mongo.handlers import MongoHandler

from hodlv2.config import LOGLEVEL, MONGODB_HOST, MONGODB_PORT
from hodlv2.worker import Worker

# Logging
logger = logging.getLogger("hodlv2")
log_level = logging.getLevelName(LOGLEVEL)
logger.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
logHandler = handlers.TimedRotatingFileHandler(
    "hodlv2/logs/hodlv2.log", when="midnight", interval=1, backupCount=30
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Log4Mongo
logger.addHandler(
    MongoHandler(
        host=MONGODB_HOST,
        port=MONGODB_PORT,
        database_name="hodlv2",
        capped=True,
    )
)

# check min. python version
if sys.version_info < (3, 8):
    ERROR_MSG = "Bot stopped! HODLv2 requires Python version >= 3.8"
    logger.critical(ERROR_MSG)
    sys.exit(ERROR_MSG)

if __name__ == "__main__":
    worker = Worker()
    worker.worker()
