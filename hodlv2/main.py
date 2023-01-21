#!/usr/bin/env python3
# pylint: disable=no-name-in-module,consider-using-with,broad-except
"""
Main worker class
"""

import logging
import sys
import time
from logging import handlers

import requests
import yaml
from log4mongo.handlers import BufferedMongoHandler
from schema import Optional, Or, Regex, Schema, SchemaError

from hodlv2.backend.backend import Backend
from hodlv2.hodlv2bot import HODLv2Bot

# Logging
logger = logging.getLogger("hodlv2")
logger.setLevel(logging.INFO)
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

        self.config = self.load_config()
        self.backend = Backend(self.config)
        self.validate_config(self.config)
        self.version_check()
        self.bot = HODLv2Bot(self.config)
        self.markets = self.config["BotSettings"].keys()

        # Log4Mongo
        logger.addHandler(
            BufferedMongoHandler(
                host=self.config["MongoDbSettings"]["Host"],
                port=self.config["MongoDbSettings"]["Port"],
                database_name="hodlv2",
                capped=True,
                buffer_size=50,
                buffer_periodical_flush_timing=10.0,
            )
        )

    def version_check(self):
        """
        TO DO
        """

        self.version = "2023.1"

        start_msg = f"Starting HODLv2 {self.version}"
        print(start_msg)
        logger.info("\n")
        logger.info(start_msg)

        # Check for new version
        try:
            url = "https://api.github.com/repos/p0ntsNL/hodlv2/releases/latest"
            req = requests.get(url, timeout=5)
            rtn = req.json()["tag_name"]
        except Exception as error:
            version_msg = (
                f"Unable to retrieve latest HODLv2 version, please try again! {error}"
            )
            logger.critical(version_msg)
            sys.exit(version_msg)

        if self.version != rtn:
            version_msg = (
                f"A new version of HODLv2 is available, please update to version {rtn}."
            )
            logger.critical(version_msg)
            sys.exit(version_msg)

    def load_config(self):
        """
        TO DO
        """

        config_path = "hodlv2/config/config.yaml"

        try:
            config_file = open(config_path, "r", encoding="utf8")
            data = yaml.load(config_file.read(), Loader=yaml.FullLoader)
            config_file.close()
            return data
        except Exception as error:
            crit_msg = f"Bot stopped! Unable to open {config_path}: {error}"
            logger.critical(crit_msg)
            sys.exit(crit_msg)

    def validate_int(self, field):
        """TO DO"""
        return f"The {field} field must have an integer value."

    def validate_int_float(self, field):
        """TO DO"""
        return f"The {field} field must have an integer or float value."

    def validate_str(self, field):
        """TO DO"""
        return f"The {field} field must have a string value."

    def validate_true_false(self, field):
        """TO DO"""
        return f"The {field} field must be 'true' or 'false'."

    def validate_buy_sell(self, field):
        """TO DO"""
        return f"The {field} field must be 'buy' or 'sell'."

    def validate_loglevel(self, field):
        """TO DO"""
        return f"The {field} field must be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'."

    def validate_market(self):
        """TO DO"""
        return "The market field must be formated like this: BTC/USD, DOT/BTC etc."

    def validate_config(self, configuration):
        """
        TO DO
        """

        config_schema = Schema(
            {
                "ExchangeSettings": {
                    "Exchange": Or(str, error=self.validate_str("Exchange")),
                    "ExchangeKey": Or(str, error=self.validate_str("ExchangeKey")),
                    "ExchangeSecret": Or(
                        str, error=self.validate_str("ExchangeSecret")
                    ),
                    "ExchangePassword": Or(
                        str, error=self.validate_str("ExchangePassword")
                    ),
                },
                "BotSettings": {
                    Optional(Regex(r"^\S+/\S+$")): {
                        "Side": Or("buy", "sell", error=self.validate_buy_sell("Side")),
                        "MaxTrades": Or(int, error=self.validate_int("MaxTrades")),
                        "TradeValue": Or(
                            int, float, error=self.validate_int("TradeValue")
                        ),
                        "PercOpen": Or(int, float, error=self.validate_int("PercOpen")),
                        "PercClose": Or(
                            int, float, error=self.validate_int("PercClose")
                        ),
                        "TakeProfitIn": Or(
                            str, error=self.validate_str("TakeProfitIn")
                        ),
                        "ResetNextTradePrice": Or(
                            int, error=self.validate_int("ResetNextTradePrice")
                        ),
                    },
                },
                "MongoDbSettings": {
                    "Host": Or(str, error=self.validate_str("Host")),
                    "Port": Or(int, error=self.validate_int("Port")),
                },
                "PushoverSettings": {
                    "PushoverEnabled": Or(
                        "true",
                        "false",
                        error=self.validate_true_false("PushoverEnabled"),
                    ),
                    "PushoverUserKey": Or(
                        str, error=self.validate_str("PushoverUserKey")
                    ),
                    "PushoverAppToken": Or(
                        str, error=self.validate_str("PushoverAppToken")
                    ),
                },
                "LoggingSettings": {
                    "LogLevel": Or(
                        "CRITICAL",
                        "ERROR",
                        "WARNING",
                        "INFO",
                        "DEBUG",
                        self.validate_loglevel("LogLevel"),
                    )
                },
            }
        )

        # Validate
        try:
            config_schema.validate(configuration)
        except SchemaError as se_error:
            logger.critical("Configuration is not valid.")
            for error in se_error.errors:
                if error:
                    logger.critical(str(error))
            for error in se_error.autos:
                if error:
                    logger.critical(str(error))
            error_msg = "Bot stopped! Configuration not valid, check the logs for more information."
            sys.exit(error_msg)

        logger.info("Configuration is valid.")

        # Send to MongoDB
        self.backend.update_one("configuration", "configuration", configuration, True)

    def reload(self):
        """
        TO DO
        """

        logger.info("\n")

        # Bot configuration
        self.config = self.load_config()
        self.validate_config(self.config)

        # Logging
        log_level = logging.getLevelName(self.config["LoggingSettings"]["LogLevel"])
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
