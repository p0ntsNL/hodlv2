# pylint: disable=broad-except
"""
TO DO
"""

import logging
import re

import requests

logger = logging.getLogger(__name__)


class Notify:
    """
    TO DO
    """

    def __init__(self, config):
        """
        TO DO
        """

        # Load config
        self.config = config

        # Force pushover
        self.notifier = "pushover"
        self.key = self.config.PUSHOVER_USER_KEY
        self.token = self.config.PUSHOVER_APP_TOKEN

    def send_pushover(self, msg):
        """
        TO DO
        """

        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={"token": self.token, "user": self.key, "message": msg, "html": 1},
                timeout=10,
            )
        except Exception as error:
            logger.error(error)

    def send(self, msg):
        """
        TO DO
        """

        # Pushover
        if self.notifier == "pushover":
            self.send_pushover(msg)
