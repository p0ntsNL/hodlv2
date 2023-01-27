#!/usr/bin/env python3
# pylint: disable=no-name-in-module,consider-using-with,broad-except
"""
Main worker class
"""

import os
import logging
import sys
import time
from logging import handlers

from hodlv2.config import MONGODB_HOST
from hodlv2.config import MONGODB_PORT
from hodlv2.config import LOGLEVEL

import requests
import yaml
from log4mongo.handlers import MongoHandler

from hodlv2.backend.backend import Backend
from hodlv2.hodlv2bot import HODLv2Bot

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

# check min. python version
if sys.version_info < (3, 8):
    ERROR_MSG = "Bot stopped! HODLv2 required Python version >= 3.8"
    logger.critical(ERROR_MSG)
    sys.exit(ERROR_MSG)


class Worker:
    """
    TO DO
    """

    def __init__(self):
        """
        TO DO
        """

        # Version check
        self.version = "2023.1"
        logger.info("")
        start_msg = f"Starting HODLv2 {self.version}"
        logger.info(start_msg)
        self.version_check()
        print(start_msg)

        # Log4Mongo
        logger.addHandler(
            MongoHandler(
                host=MONGODB_HOST,
                port=MONGODB_PORT,
                database_name="hodlv2",
                capped=True,
            )
        )

    def healthcheck(self):
        return self.health

    def version_check(self):
        """
        TO DO
        """

        # Check for new version
        try:
            url = "https://api.github.com/repos/p0ntsNL/hodlv2/releases/latest"
            req = requests.get(url, timeout=5)
            rtn = req.json()["tag_name"]
            if self.version != rtn:
                version_msg = (
                    f"A new version of HODLv2 is available, please update to version {rtn}."
                )
                logger.warning(version_msg)
        except Exception as error:
            version_msg = (
                f"Unable to retrieve latest HODLv2 version from GitHub! {error}"
            )
            logger.error(version_msg)

    def load_config(self):
        """
        TO DO
        """

        # Load v2023.1 config file if it exists and push to backend
        try:
            config_dir = "hodlv2/config"
            config_path = f"{config_dir}/config.yaml"
            if os.path.exists(config_path):
                config_file = open(config_path, "r", encoding="utf8")
                configuration = yaml.load(config_file.read(), Loader=yaml.FullLoader)
                config_file.close()
                logger.info('Loading config from config.yaml.')

                # Send config to backend and remove it afterwards
                update = self.backend.update_one("configuration", "configuration", configuration, True)
                if update[0]:
                    logger.info('Saved config to backend.')
                    if os.path.exists(config_path):
                        os.remove(config_path)
                        os.rmdir(config_dir)
        except Exception as error:
            crit_msg = f"Unable to load config from {config_path}: {error}"
            logger.critical(crit_msg)

        # Load v2023.2+ config from backend
        try:
            get_config = self.backend.find_one("configuration", "configuration")
            if get_config[0]:
                logger.info('Loading config from backend.')
                del get_config[1]['_id']
                self.config_health = True
                return get_config[1]
        except Exception as e:
            crit_msg = f"Unable to load config from backend: {error}"
            logger.critical(crit_msg)

        self.config_health = False

    def update_health(self):

        # Send config to backend and remove it afterwards
        update = self.backend.update_one("health", "health", self.health_status, True)
        if not update[0]:
            logger.info('Unable to save health data to backend.')

    def load(self):
        """
        TO DO
        """

        # Load
        self.backend = Backend()
        self.config = self.load_config()
        self.bot = HODLv2Bot(self.config)
        self.markets = self.config["BotSettings"].keys()

        # Logging
        log_level = logging.getLevelName(LOGLEVEL)
        logger.setLevel(log_level)

        # healthcheck
        self.health = True
        self.b_h = self.backend.healthcheck()
        self.e_h = self.bot.healthcheck()
        self.c_h = self.config_health
        if not self.backend.healthcheck() or not self.bot.healthcheck() or not self.config_health:
            self.health = False

        self.health_status = {
            "health": self.health,
            "backend": self.b_h,
            "exchange": self.e_h,
            "config": self.c_h,
        }
        self.update_health()

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

    def worker(self):
        """
        TO DO
        """

        iteration = 0

        while True:

            iteration += 1

            logger.info("")
            logger.info("Iteration #%s started", iteration)

            # Load
            self.load()

            # If healthy
            if self.health:

                # Reset if open or closed orders are not retrieved from exchange
                if not self.bot.open_closed_ok:
                    self.reset()
                    continue
                logger.info("Open and closed order data retrieved successfully.")

                # Loop markets
                for market in self.markets:

                    # Load market settings
                    self.bot.bot_init(market)

                    # Check if a new trade should be initiated
                    new_trade = self.bot.check_new_trade(market)
                    if new_trade[0]:

                        # Initiate new trade
                        self.bot.new_trade(market, new_trade[1])

                # Check closed orders for profit
                self.bot.check_closed_orders()

            # If unhealthy
            else:
                logger.error("Health check failure!")
                logger.error(str(self.health_status))

            # Reset
            logger.info("Iteration #%s finished", iteration)
            self.reset()


if __name__ == "__main__":

    worker = Worker()
    worker.worker()
