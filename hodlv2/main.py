#!/usr/bin/env python3
# pylint: disable=no-name-in-module
"""
Main worker class
"""

import logging
import sys
import time
from logging import handlers

import yaml
from schema import Optional, Or, Regex, Schema, SchemaError

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

        # Bot configuration
        self.config = self.load_config()
        self.validate_config(self.config)

        # Logging
        log_level = logging.getLevelName(self.config["LoggingSettings"]["LogLevel"])
        logger.setLevel(log_level)

        self.version = "HODLv2 2023.1"
        logger.info("\n")
        logger.info("Starting %s", self.version)
        print(f"Starting {self.version}")

        self.notify = Notify(self.config)
        self.bot = HODLv2Bot(self.config)

        self.markets = self.config["BotSettings"].keys()

    def load_config(self):
        """
        TO DO
        """

        config_path = "hodlv2/config/config.yaml"

        try:
            config_file = open(config_path, "r")
            data = yaml.load(config_file.read(), Loader=yaml.FullLoader)
            config_file.close()
            return data
        except Exception as error:
            logger.critical(f"Unable to open {config_path}: {error}")
            sys.exit(f"Unable to open {config_path}: {error}")

    def validate_int(self, field):
        return f"The {field} field must have an integer value."

    def validate_int_float(self, field):
        return f"The {field} field must have an integer or float value."

    def validate_str(self, field):
        return f"The {field} field must have a string value."

    def validate_true_false(self, field):
        return f"The {field} field must be 'true' or 'false'."

    def validate_buy_sell(self, field):
        return f"The {field} field must be 'buy' or 'sell'."

    def validate_loglevel(self, field):
        return f"The {field} field must be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'."

    def validate_market(self):
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
            sys.exit("Configuration is not valid, check the logs for more information.")

        logger.info("Configuration is valid.")

    def reload(self):
        """
        TO DO
        """

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
