from pymongo import MongoClient
import configuration

connection_params = configuration.connection_params
mongoconnection = MongoClient(
    'mongodb://{host}:{port}/'.format(**connection_params)
)
db = mongoconnection.hodlv2
