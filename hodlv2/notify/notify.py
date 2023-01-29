# pylint: disable=broad-except
"""
TO DO
"""

import logging

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

    def send_pushover(self, msg):
        """
        TO DO
        """

        # Variables
        enabled = self.config["PushoverSettings"]["PushoverEnabled"]
        key = self.config["PushoverSettings"]["PushoverUserKey"]
        token = self.config["PushoverSettings"]["PushoverAppToken"]

        # Only send when enabled
        if str(enabled) != "true":
            return

        # Send pushover
        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={"token": token, "user": key, "message": msg, "html": 1},
                timeout=10,
            )
        except Exception as error:
            logger.debug("Unable to send pushover: %s", error)

    def send(self, msg):
        """
        TO DO
        """

        # Pushover
        if self.notifier == "pushover":
            self.send_pushover(msg)
