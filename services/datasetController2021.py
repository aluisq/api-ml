import os
import pymongo
from dotenv import load_dotenv
from bson.json_util import dumps

# Carrega as configurações da variável de ambiente
load_dotenv()

# MongoDb
path_mongo = os.getenv('MONGO_CONNECTION')
client = pymongo.MongoClient(path_mongo)
db_transito = client.db.transito2021


def getDataset():
    data = []

    dataset = db_transito.find()

    for json in dataset:
        data.append(json)

    # data_json = dumps(data, indent=2)

    return data
