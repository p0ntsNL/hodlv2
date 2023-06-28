#!/usr/bin/env python3
# pylint: disable=broad-except
"""
Worker class
"""

import logging
import time

from hodlv2.backend.backend import Backend
from hodlv2.bot import Bot
from hodlv2.configuration import Configuration
from hodlv2.misc import version_check

logger = logging.getLogger(__name__)


class Worker:
    """
    Worker class
    """

    def __init__(self):
        """
        Init all veriables and objects the class needs to work
        """

        # Variables
        self.health = True

        # Version check
        version_check()

        # Objects
        self.backend = Backend(verify_indexes=True)
        self.configuration = Configuration()
        self.bot = Bot(self.configuration.config, init=True)
        self.markets = self.configuration.config["BotSettings"].keys()

        # Health
        self.health_status = {
            "health": True,
            "backend": self.backend.health,
            "exchange": self.bot.exchange_health,
            "config": self.configuration.health,
        }
        for status in self.health_status.values():
            if not status:
                self.health_status["health"] = status

        # Update health to database
        if self.backend.health:
            self.update_health()

    def update_health(self):
        """
        Update health data to the backend.
        """

        # Send config to backend and remove it afterwards
        update = self.backend.update_one("health", "health", self.health_status, True)
        if update[0]:
            logger.info("Health data saved to backend.")

    def reload(self):
        """
        Load variables and objects needed by the bot on each iteration.
        Copy of __init__
        """

        # Variables
        self.health = True

        # Objects
        self.backend = Backend(verify_indexes=True)
        self.configuration = Configuration()
        self.bot = Bot(self.configuration.config)
        self.markets = self.configuration.config["BotSettings"].keys()

        # Health
        self.health_status = {
            "health": True,
            "backend": self.backend.health,
            "exchange": self.bot.exchange_health,
            "config": self.configuration.health,
        }
        for status in self.health_status.values():
            if not status:
                self.health_status["health"] = status

        # Update health to database
        if self.backend.health:
            self.update_health()

    def sleep(self):
        """
        Sleep 10 second for each configured market on each iteration.
        To make sure exchange API limitations are not reached.
        """

        logger.info(
            "Sleeping for %s seconds now, it is save to stop me during my sleep!",
            len(self.markets) * 10,
        )
        time.sleep(len(self.markets) * 10)

    def worker(self):
        """
        This function will initiate the bot and iterate.
        """

        iteration = 0

        while True:
            iteration += 1

            logger.info("")
            logger.info("Iteration #%s started", iteration)

            # Load
            self.reload()

            # If healthy
            if self.health_status["health"]:
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

            logger.info("Iteration #%s finished", iteration)
            self.sleep()
