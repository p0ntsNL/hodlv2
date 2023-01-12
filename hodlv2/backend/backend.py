# pylint: disable=broad-except
"""
Main backend class.
Currently defaults to MongoDB which is the only backend available.
"""

import logging

from pymongo import MongoClient

from hodlv2.notify.notify import Notify

logger = logging.getLogger(__name__)


class Backend:
    """
    Backend class
    """

    def __init__(self, config):
        """
        Init all variables and objects the class needs to work
        """

        # Load config
        self.config = config

        # MongoDB
        self.client = MongoClient("localhost", 27017)
        self._db = self.client["hodlv2"]

        # Notify
        self.notify = Notify(self.config)

    def find_one(self, collection, _id):
        """
        Find a document by ID in a MongoDB collection.
        :param collection: name of the collection to use
        :param _id: id of the document to search for
        """

        try:
            find = self._db[collection].find_one(_id)
            if not isinstance(find, type(None)):
                return True, find
        except Exception as error:
            logger.error(f"find_one error: {error}")

        logger.debug(f"find_one: Unable to find {_id} in {collection}.")
        return False, {}

    def find_one_exists(self, collection, _id, key, exists):
        """
        Find a document by ID in a MongoDB collection, but only if a certain key exists.
        :param collection: name of the collection to use
        :param _id: id of the document to search for
        :param key: key that needs to be checked for existance
        :param exists: needs to exist True or False
        """

        try:
            find = self._db[collection].find_one({"_id": _id, key: {"$exists": exists}})
            if not isinstance(find, type(None)):
                return True, find
        except Exception as error:
            logger.error(f"find_one_exists error: {error}")

        logger.debug(f"find_one_exists: Unable to find {_id} in {collection}.")
        return False, {}

    def update_one(self, collection, _id, data, upsert):
        """
        Update a document by ID in a MongoDB collection.
        :param collection: name of the collection to use
        :param _id: id of the document to update
        :param data: data to update the document with
        :param upsert: wether or not a new document should be created if it does not exist yet
        """

        try:

            update = self._db[collection].update_one(
                {"_id": _id}, {"$set": data}, upsert=upsert
            )
            modified_count = update.modified_count
            upserted_id = update.upserted_id

            if modified_count == 1 or not isinstance(upserted_id, type(None)):
                return True, {}
        except Exception as error:
            logger.error(f"update_one error: {error}")

        logger.debug(f"update_one: Unable to update {_id} in {collection}.")
        return False, {}

    def insert_one(self, collection, data):
        """
        Insert a document to a MongoDB collection.
        :param collection: name of the collection to use
        :param data: data to insert the document with
        """

        try:
            insert = self._db[collection].insert_one(data)
            inserted_id = insert.inserted_id
            if inserted_id == data["_id"]:
                return True, {}
        except Exception as error:
            logger.error(f"insert_one error: {error}")

        logger.debug(f"insert_one: Unable to insert trade in {collection}.")
        return False, {}
