#!/usr/bin/env python3
# pylint: disable=import-error
"""
TO DO
"""

import importlib
import sys
import time

from hodlv2 import __version__
from hodlv2.config import config
from hodlv2.hodlv2bot import HODLv2Bot
from hodlv2.notify.notify import Notify

# check min. python version
if sys.version_info < (3, 8):
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
        self.notify = Notify(self.config)

        self.version = f"HODLv2 {__version__}"
        self.notify.send(self.version, "INFO", logging_only=True)
        print (self.version)

        self.bot = HODLv2Bot(self.config)

    def reload(self):
        """
        TO DO
        """

        # Bot configuration
        self.config = importlib.reload(config)

        # Init bot
        self.bot = HODLv2Bot(self.config)

    def sleep(self):
        """
        TO DO
        """

        return len(self.config.MARKETS) * 10

    def reset(self):
        """
        TO DO
        """

        time.sleep(self.sleep())
        self.reload()

    def worker(self):
        """
        TO DO
        """

        while True:

            # Reset if open or closed orders are not retrieved from exchange
            if not self.bot.open_closed_ok:
                self.reset()
                continue

            # Loop markets
            for market in self.config.MARKETS:

                # Check if a new trade should be initiated
                new_trade = self.bot.check_new_trade(market)
                if new_trade[0]:

                    # Initiate new trade
                    self.bot.new_trade(market, new_trade[1])

            # Check closed orders for profit
            self.bot.check_closed_orders()

            # Reset
            self.reset()


if __name__ == "__main__":

    worker = Worker()
    worker.worker()
