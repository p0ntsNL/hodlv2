#!/usr/bin/env python3
# pylint: disable=broad-except,too-few-public-methods
"""
Configuration class
"""

import logging
import os

import yaml

from hodlv2.backend.backend import Backend

logger = logging.getLogger(__name__)


class Configuration:
    """
    Worker class
    """

    def __init__(self):
        """
        Init all veriables and objects the class needs to work
        """

        # Variables
        self.health = True
        self.default_config = {
            "_id": "configuration",
            "BotSettings": {},
            "ExchangeSettings": {
                "Exchange": "kraken",
                "ExchangeKey": "",
                "ExchangeSecret": "",
                "ExchangePassword": "",
            },
            "PushoverSettings": {
                "PushoverEnabled": "false",
                "PushoverUserKey": "",
                "PushoverAppToken": "",
            },
            "PushbulletSettings": {
                "PushbulletEnabled": "false",
                "PushbulletApiKey": "",
            },
        }

        # Objects
        self.backend = Backend()
        self.config = self.load_config()

    def load_config(self):
        """
        Load config from hodlv2/config.yaml if it exists (pre-web), move config over to the backend.
        Otherwise load from backend directly.
        """

        # Load v2023.1 config file if it exists and push to backend
        try:
            config_dir = "hodlv2/config"
            config_path = f"{config_dir}/config.yaml"
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf8") as config_file:
                    configuration = yaml.load(
                        config_file.read(), Loader=yaml.FullLoader
                    )
                logger.info("Loading config from config.yaml.")

                # Send config to backend and remove it afterwards
                update = self.backend.update_one(
                    "configuration", "configuration", configuration, True
                )
                if update[0]:
                    logger.info("Saved config to backend.")
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
                logger.info("Loading config from backend.")
                return get_config[1]

            # If no configuration is found, use and save the default configuration
            if isinstance(get_config[0], type(None)):

                logger.info("No config found in the backend, using default config.")

                # Send config to backend and remove it afterwards
                update = self.backend.update_one(
                    "configuration", "configuration", self.default_config, True
                )
                if update[0]:
                    logger.info("Saved default config to backend.")

                return self.default_config

        except Exception as error:
            crit_msg = f"Unable to load config from backend: {error}"
            logger.critical(crit_msg)

        self.health = False
        return None
