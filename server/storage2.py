from pymongo import MongoClient, TEXT, InsertOne, DeleteMany, ReplaceOne, UpdateOne
from bson.objectid import ObjectId
from bson import json_util
import json
import visual_utils
from pprint import pprint
from datetime import datetime
import time
import StatGen
import os
import pretty
import n_rank as nr
import pymongo
from pprint import pprint


# --default port is : 27017
print("in storage 2")
with open(os.environ['MONGO_CLIENT']) as f:
    entry = f.read()
client = MongoClient(entry)
db = client.get_database('cache_trace')


def find_in_collection(collection_name, param=None):
    collec = db[collection_name]
    result = []
    if param == None:
        for items in collec.find():
            result.append(items)
    else:
        for items in collec.find({param[0]: param[1]}):
            result.append(items)
    return result


def insert_to_collection(collection_name, data):
    collection = db[collection_name]
    
    result = collection.insert_one(data)

    if result == None:
        return False
    else:
        return result.inserted_id


def delete_one_from_collection(collection_name, field, value):
    collec = db[collection_name]
    result = collec.delete_one({field: value})
    return result

def delete_many_from_collection(collection_name, field, value):
    collec = db[collection_name]
    collec.delete_many({field: value})
    return result

def find_distinct_fields(collection_name, field):
    collec = db[collection_name]
    vals = []
    for distinct_val in collec.find().distinct(field):
        vals.append(distinct_val)
    return vals

def find_in_collection_multi(collection_name, field_list):
    collec = db[collection_name]
    result = []

    iterable = collec.find({"$and": 
                            field_list})
                
    data_set_records = [items for items in iterable]

    return data_set_records

#after around 80 inserts in quick succession mongo begins to slow down what it receives so it is necessary to use bulkwrite
def insert_many(collection_name, data_list):
    collec = db[collection_name]
    workload = []
    result = None
    for entries in data_list:
        workload.append(InsertOne(new_trace) )
    try:
        result = collec.bulk_write(workload, ordered=False)
    except pymongo.errors.BulkWriteError as bwe:
        print("error uploading a file")
        pass

    print("finished inserting everything")
    return result.bulk_api_result




if __name__ == "__main__":
    print('what')