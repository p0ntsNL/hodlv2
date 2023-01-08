#!/usr/bin/python3.10

import logging
import re

import config
import requests


class Notify:
    def __init__(self):

        # Load config
        self.config = config

        # Logging
        self.logger = logging
        self.logger.basicConfig(
            filename="hodlv2.log",
            format="%(asctime)s | %(levelname)s | %(message)s",
            level=logging.INFO,
        )

        # Force pushover
        self.notifier = "pushover"
        self.key = self.config.PUSHOVER_USER_KEY
        self.token = self.config.PUSHOVER_APP_TOKEN

    def send_logging(self, msg, loglevel):

        if loglevel == "INFO":
            self.logger.info(msg)
        elif loglevel == "WARNING":
            self.logger.warning(msg)
        elif loglevel == "CRITICAL":
            self.logger.critical(msg)
        elif loglevel == "ERROR":
            self.logger.error(msg)
        elif loglevel == "DEBUG":
            self.logger.debug(msg)

    def send_pushover(self, msg):

        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={"token": self.token, "user": self.key, "message": msg, "html": 1},
            )
        except Exception as e:
            self.send_logging(e, "ERROR")

    def send(self, msg, loglevel, logging_only=False):

        # Remove HTML
        msg = msg.replace("<br><br>", " | ")
        msg = msg.replace("<br>", " | ")
        msg = re.sub("<[^<]+?>", "", msg)

        # Logger
        self.send_logging(msg, loglevel)

        if not logging_only:

            # Pushover
            if self.notifier == "pushover":
                self.send_pushover(msg)
