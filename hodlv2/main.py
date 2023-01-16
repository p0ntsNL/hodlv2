#!/usr/bin/env python3
# pylint: disable=import-error,no-name-in-module
"""
Main worker class
"""

import importlib
import logging
import sys
import time
from logging import handlers

from hodlv2.config import config
from hodlv2.hodlv2bot import HODLv2Bot
from hodlv2.notify.notify import Notify

# Logging
logger = logging.getLogger("hodlv2")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
logHandler = handlers.TimedRotatingFileHandler(
    "hodlv2/hodlv2.log", when="midnight", interval=1, backupCount=30
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# check min. python version
if sys.version_info < (3, 8):
    logger.critical("HODLv2 required Python version >= 3.8")
    sys.exit("HODLv2 requires Python version >= 3.8")


class Worker:
    """
    TO DO
    """

    def __init__(self):
        """
        TO DO
        """

        self.config = config

        # Logging
        log_level = logging.getLevelName(self.config.LOG_LEVEL)
        logger.setLevel(log_level)

        self.version = "HODLv2 2023.1"
        logger.info("\n")
        logger.info("Starting %s", self.version)
        print(f"Starting {self.version}")

        self.notify = Notify(self.config)
        self.bot = HODLv2Bot(self.config)

        self.markets = self.config.MARKETS.keys()

    def reload(self):
        """
        TO DO
        """

        # Bot configuration
        self.config = importlib.reload(config)

        # Logging
        log_level = logging.getLevelName(self.config.LOG_LEVEL)
        logger.setLevel(log_level)

        # Init bot
        self.bot = HODLv2Bot(self.config)

    def sleep(self):
        """
        TO DO
        """

        return len(self.markets) * 10

    def reset(self):
        """
        TO DO
        """

        logger.info(
            "Sleeping for %s seconds now, it is save to stop me during my sleep!",
            self.sleep(),
        )
        time.sleep(self.sleep())
        self.reload()

    def worker(self):
        """
        TO DO
        """

        iteration = 0

        while True:

            iteration += 1

            logger.info("\n")
            logger.info("Iteration #%s started", iteration)

            # Reset if open or closed orders are not retrieved from exchange
            if not self.bot.open_closed_ok:
                self.reset()
                continue

            # Loop markets
            for market in self.markets:

                # Load market settings
                self.bot.bot_settings(market)

                # Check if a new trade should be initiated
                new_trade = self.bot.check_new_trade(market)
                if new_trade[0]:

                    # Initiate new trade
                    self.bot.new_trade(market, new_trade[1])

            # Check closed orders for profit
            self.bot.check_closed_orders()

            # Reset
            logger.info("Iteration #%s finished", iteration)
            self.reset()


if __name__ == "__main__":

    worker = Worker()
    worker.worker()
