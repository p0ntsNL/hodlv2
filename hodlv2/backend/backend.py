# pylint: disable=broad-except
"""
Backend class.
The backend class connects to the configured database.
Currently defaults to MongoDB which is the only backend available.
"""

import logging

import pymongo

from hodlv2.config import MONGODB_HOST, MONGODB_PORT

logger = logging.getLogger(__name__)


class Backend:
    """
    Backend class
    """

    def __init__(self, verify_indexes=False):
        """
        Init all variables and objects the class needs to work
        """

        # Variables
        self.health = True

        # MongoDB
        try:
            self.host = MONGODB_HOST
            self.port = MONGODB_PORT
            self.client = pymongo.MongoClient(
                self.host,
                self.port,
            )
            self._db = self.client["hodlv2"]
            stats = self._db.command("dbstats")
            if stats["ok"] != 1:
                raise SystemError("MongoDB hodlv2 database status failed.")
        except Exception as error:
            msg = f"Unable to connect to MongoDB: {error}"
            logger.critical(msg)
            self.health = False
        else:

            # Verify indexes
            if verify_indexes:
                self.verify_mongodb_indexes()

    def verify_mongodb_indexes(self):
        """
        Make sure MongoDB indexes exist.
        """

        try:
            indexes = self._db["trades"].index_information()
            if "profit_currency_1_profit_1_status_1" not in indexes:
                print("hier")
                self._db["trades"].create_index(
                    [
                        ("profit_currency", pymongo.ASCENDING),
                        ("profit", pymongo.ASCENDING),
                        ("status", pymongo.ASCENDING),
                    ]
                )
            if "profit_currency_1_profit_perc_1_status_1" not in indexes:
                self._db["trades"].create_index(
                    [
                        ("profit_currency", pymongo.ASCENDING),
                        ("profit_perc", pymongo.ASCENDING),
                        ("status", pymongo.ASCENDING),
                    ]
                )
            if "trades_1" not in indexes:
                self._db["trades"].create_index(
                    [
                        ("fees", pymongo.ASCENDING),
                    ]
                )
            if "status_1" not in indexes:
                self._db["trades"].create_index(
                    [
                        ("status", pymongo.ASCENDING),
                    ]
                )
        except Exception as error:
            msg = f"Unable to verify MongoDB indexes: {error}"
            logger.critical(msg)
            self.health = False

    def find(self, collection, first, second):
        """
        Find a document by ID in a MongoDB collection.
        :param collection: name of the collection to use
        :param data: data of the documents to search for
        """

        try:
            find = self._db[collection].find(first, second)
            if not isinstance(find, type(None)):
                return True, find
        except Exception as error:
            logger.debug("find error: %s", error)

        logger.debug("find: Unable to find %s and %s in %s.", first, second, collection)
        return False, {}

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
            return None, {}
        except Exception as error:
            logger.debug("find_one error: %s", error)

        logger.debug("find_one: Unable to find %s in %s.", _id, collection)
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
            logger.debug("find_one_exists error: %s", error)

        logger.debug("find_one_exists: Unable to find %s in %s.", _id, collection)
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
            logger.debug("update_one error: %s", error)

        logger.debug("update_one: Unable to update %s in %s.", _id, collection)
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
            logger.debug("insert_one error: %s", error)

        logger.debug("insert_one: Unable to insert trade in %s.", collection)
        return False, {}

    def aggregate(self, collection, sort=None, match=None, group=None):

        """
        Aggregate data based on search query..
        :param collection: name of the collection to use
        :param match: match a certain key/value
        :param group: group data in specific groups based on key/value
        """

        data = []

        if sort:
            data.append(sort)
        if match:
            data.append(match)
        if group:
            data.append(group)

        try:
            aggregate = self._db[collection].aggregate(data)
            if aggregate:
                return True, aggregate
        except Exception as error:
            logger.debug("aggregate error: %s", error)

        logger.debug("aggregate: Unable to aggregate data in %s.", collection)
        return False, {}

    def count_documents(self, collection, criteria):
        """
        Count documents based on search criteria in a MongoDB collection.
        :param collection: name of the collection to use
        :param criteria: criteria of the documents to search for
        """

        try:
            count = self._db[collection].count_documents(criteria)
            return True, count
        except Exception as error:
            logger.debug("count_documents error: %s", error)

        logger.debug("count_documents: Unable to find %s in %s.", criteria, collection)
        return False, {}
