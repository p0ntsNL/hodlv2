import configuration
from pymongo import MongoClient

connection_params = configuration.connection_params
mongoconnection = MongoClient("mongodb://{host}:{port}/".format(**connection_params))
db = mongoconnection.hodlv2
