# pylint: disable=broad-except
"""
Notify class.
The notify class sends trade update notifications.
Currently defaults to Pushover which is the only on available.
"""

import logging

import requests

logger = logging.getLogger(__name__)


class Notify:
    """
    Notify class
    """

    def __init__(self, config):
        """
        Init all variables and objects the class needs to work
        """

        # Load config
        self.config = config

        # Force pushover
        self.notifier = "pushover"

    def send_pushover(self, msg):
        """
        Send pushover.
        :param msg: The message to send.
        """

        # Variables
        enabled = self.config["PushoverSettings"]["PushoverEnabled"]
        key = self.config["PushoverSettings"]["PushoverUserKey"]
        token = self.config["PushoverSettings"]["PushoverAppToken"]

        # Only send when enabled
        if str(enabled) != "true":
            return

        # Send
        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={"token": token, "user": key, "message": msg, "html": 1},
                timeout=10,
            )
        except Exception as error:
            logger.debug("Unable to send pushover: %s", error)

    def send_pushbullet(self, msg):
        """
        Send pushbullet.
        :param msg: The message to send.
        """

        # Variables
        enabled = self.config["PushbulletSettings"]["PushbulletEnabled"]
        key = self.config["PushbulletSettings"]["PushbulletApiKey"]

        # Only send when enabled
        if str(enabled) != "true":
            return

        # Send
        try:
            url = "https://api.pushbullet.com/v2/pushes"
            headers = {"content-type": "application/json", "Authorization": 'Bearer '+key}
            data = {"type": "note", "title": "HODLv2", "body": msg}
            requests.post(url,
                headers=headers,
                data=json.dumps(data),
                timeout=10,
            )
        except Exception as error:
            logger.debug("Unable to send pushbullet: %s", error)

    def send(self, msg):
        """
        Catch all that distributes requests to specific notification types.
        :param msg: The message to send.
        """

        # Pushover
        if self.notifier == "pushover":
            self.send_pushover(msg)
        elif self.notifier == "pushbullet":
            self.send_pushbullet(msg)
