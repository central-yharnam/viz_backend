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
client = MongoClient("mongodb+srv://user_1:ravioli@cluster0-fiuhd.azure.mongodb.net/test?retryWrites=true&w=majority")
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
    #print(db.algorithm_specs.find())

#input: trace name
#output: print all items in the trace_runs collection that have the trace name passed as an argument
'''def find_all_run_specs(trace_name):
    runs = db.trace_runs
    for items in runs.find({'trace':trace_name}):
        print(items)
'''

'''def delete_workload(trace):
    pretty.utility("DELETING WORKLOAD: ", trace)
    workloads = db.workload
    workloads.delete_many(trace)'''

'''def delete_trace_runs(param):
    pretty.utility("delete trace run")
    runs = db.trace_runs
    runs.delete_many(param)'''

def delete_plots_tracked(param):
    pretty.utility("deleting plots with param: ", param)
    plots = db.plots_tracked
    plots.delete_many({'flag': param})

def store_flag(flag, param_list):
    plots = db.plots_tracked
    plots_obj = plots.find_one({'flag': flag})

    if plots_obj == None:
        pretty.utility("plot not found, adding to mongo")
        plot_data = {}
        plot_data['flag'] = flag
        plot_data['params'] = param_list
        plots.insert_one(plot_data)
    else:
        pretty.success(flag, param_list, "already present")

def del_all():
    print("in del all")
    work = db.workload
    trace = db.trace_runs
    heat_work = db.workload
    alg = db.alg_runs
    con = alg.configs

    arr = [work, trace, heat_work, alg, con]
    for items in arr:
        entries = items.find()
        for res in entries:
            iden = res.get("_id")
            items.delete_many({"_id": iden})

def heat_map_wipe():
    heat = db.workload
    algruns = db.alg_runs
    dataset = db.dataset

    heat.delete_many({ "delete" : True} )
    algruns.delete_many({ "final pollution" : None} )
    archetypes = ['FIU', 'CloudCache', 'CloudVPS', 'MSR', 'CloudPhysics']
    for ac in archetypes:
        print(ac)
        '''new_arch = {
        'workload_ids': [],
        'dataset': ac
        }'''
        dataset.delete_many({"dataset": ac})
        #archtrace.insert_one(new_arch)
    print("everything deleted")



def heat_map_find(algorithms, cache_size, dataset):

    print("in heatmap find")
    algruns = db.alg_runs
    heat_map_records = []
    for archs in dataset:
        #print("hello?")
        #a = algruns.find({'dataset': archs})
        #container = [things for things in a]
        #print(container)
        for alg in algorithms:
            #print("hello2")
            #a = algruns.find({"$and":[{'dataset': archs},{"cache_size": size}]})
            #container = [things for things in a]
            #print(container)
            for size in cache_size:
                #print("hello3")
                #algruns.find_many({"dataset": ac})
                iterable = algruns.find({"$and": 
                          [{"dataset": archs}, 
                          {"cache_size": size},
                          {"algorithm": alg}
                          ]})
                
                data_set_records = [items for items in iterable]
                heat_map_records.extend(data_set_records)
    print("finished heatmap find")

    #records = [print(rec) for rec in heat_map_records]
    #print(records)
    return heat_map_records

def update_arch_traces():
    algruns = db.alg_runs
    archtrace = db.archtrace
    archetypes = ['FIU', 'CloudCache', 'CloudVPS', 'MSR', 'CloudPhysics']
    #dicts = {}
    

    for archs in archetypes:
        iterable = algruns.find({"dataset": archs}, {"_id": 1})

        arch_records = [items for items in iterable]
        #print(arch_records)
        #dicts[archs] = arch_records
        archtrace.update_one({'dataset': archs}, {'$push': {'workload_ids': { '$each': arch_records }}})

def update_cache_sizes():
    algruns = db.alg_runs
    print("sup")
    #print(heat.find())
    for testy in algruns.find().distinct('cache_size'):
        print(testy)
        iterable = algruns.find({"cache_size": testy}, {"_id": 1})
        cs_rescords = [items for items in iterable]

def update_algs():
    algruns = db.alg_runs
    print("sup")
    #print(heat.find())
    for testy in algruns.find().distinct('algorithm'):
        print(testy)

#
def update_collection(field):
    algruns = db.alg_runs
    collec = db[field]
    collec.create_index([(field, 1)], unique=True)
    print("sup")
    print(field)
    #collec.insert_one({'test': 'hello?'})
    #collec.delete_many({"test": 'hello?'})
    #print(heat.find())
    for distinct_val in algruns.find().distinct(field):
        print(distinct_val)
        iterable = algruns.find({field: distinct_val}, {"_id": 1})
        field_records = [items for items in iterable]
        #collec.update_one({field: distinct_val}, {'$push': {'workload_ids': { '$each': field_records }}})
        category =  {}
        category['workload_ids'] = field_records
        category[field] = distinct_val
        collec.insert_one(category)

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

    if result = None:
        return False
    else:
        return result.inserted_id




#return all 


# finds all distinct algorithms, cache sizes and archtraces (also known as datasets) in the algruns collection.
# this is for the config builder. 
def distinct_fields_available():
    algruns = db.alg_runs
    a = ['algorithm', 'cache_size', 'dataset']
    result = {}
    current_vals = []
    for field in a:
        for distinct_val in algruns.find().distinct(field):
            current_vals.append(distinct_val)
        result[field] = current_vals
        current_vals = []
    return result


def heat_map_test():
    print("in heat map test")
    heat = db.workload
    #print(a)
    #heat.drop_index('trace name')

    algruns = db.alg_runs
    archtrace = db.archtrace
    #heat.drop_index([('trace name', TEXT)])
    heat.create_index([('trace name', 1)], unique=True)


    #algruns.drop_index([('trace name', 1), ('algorithm', 1), ('dataset', 1), ('cache_size', 1)])
    algruns.create_index([('trace name', 1), ('algorithm', 1), ('dataset', 1), ('cache_size', 1)], unique=True)

    trace_list = nr.p_csv()
    #traces = db.workload
    to_workload = []

    archetypes = ['FIU', 'CloudCache', 'CloudVPS', 'MSR', 'CloudPhysics']
    '''for ac in archetypes:
        print(ac)
        new_arch = {
        'workload_ids': [],
        'dataset': ac
        }
        archtrace.insert_one(new_arch)'''
        #archtrace.delete_many({"dataset": ac})
    workload = []
    algs_ran = []

    dataset_archs = {}
    
    for traces in trace_list:

        new_trace = {
        'trace name' : traces['traces'],
        'requests' : traces['hits'] + traces['misses'],
        'unique' : traces['size']/traces['cache_size'],
        'reuses' : None,
        'writes' : traces['writes'],
        'requests uploaded to minio': False,
        'request frequency uploaded to minio' : False,
        'delete': True,
        'dataset': traces['dataset']
        }
        workload.append(InsertOne(new_trace) )

        trace_data = {}
        trace_data['trace name'] = traces['traces']
        trace_data['algorithm'] = traces['algo']
        trace_data['cache_size'] = traces['cache_size']
        trace_data['date'] = datetime.now()
        trace_data['ios'] = traces['hits'] + traces['misses']
        trace_data['total hits'] = traces['hits']
        trace_data['final hit rate'] = traces['hit_rate']
        trace_data['final misses'] = traces['misses']
        trace_data['final pollution'] = None
        trace_data['hit rate array uploaded to minio'] = False
        trace_data['miss rate array uploaded to minio'] = False
        trace_data['pollution array uploaded to minio'] = False
        trace_data['dataset'] = traces['dataset']
        algs_ran.append( InsertOne(trace_data) )
        
        '''if dataset_archs.get(traces['dataset']):
            
            dataset_archs[traces['dataset']].append(traces['traces'])
        else:
            dataset_archs[traces['dataset']] = []
            dataset_archs[traces['dataset']].append(traces['traces'])'''

    #print(workload)
    #print(algs_ran)
    #print(dataset_archs)

    '''try:
        ye = heat.insert_many(workload, ordered=False)
    except pymongo.errors.BulkWriteError:
        pass'''

    '''try:
        ye = heat.insert_many(workload, ordered=False)
    except pymongo.errors.BulkWriteError as bwe:
        err = sum(1 for _ in filter(lambda x: x['code'] != 11000, bwe.details['writeErrors']))
        if err > 0:
            raise'''
    try:
        heat.bulk_write(workload, ordered=False)
    except pymongo.errors.BulkWriteError as bwe:
        #pprint(bwe.details)
        pass
        
    try:
        algruns.bulk_write(algs_ran, ordered=False)
    except pymongo.errors.BulkWriteError as bwe:
        #pprint(bwe.details)
        pass
    print("finished inserting everything")


"""
    gets a "graph key" object from minio
    - a dict of graph types, with graph's flag and
    parameters for each
    each graph should have:
        source (source of data - workload, algorithm, etc)
        graph_type (line, scatter, or histogram)
        minio_flag
        x_label
        y_label
        title
        algorithm_specific (bool, is graph type only 
            available for certain algorithms?)
"""
def get_graph_key():
    gr_types = db.graph_types
    key = gr_types.find_one({"name": "graph type key"})
    #json_key = json.dumps(key)
    del key['_id']
    del key['name']
    return key


def update_desc():
    datasets = []
    algruns = db.alg_runs
    workload = db.workload
    data = db.dataset

    descriptions = {'FIU': """End user/ developer home directories; Web server for faculty/staff/students;
    Apache webserver for research projects; Web interface for the mail server; On-line course management system """, 'CloudCache': """Online course management website; Web server for a CS department user web-
    pages""", "CloudVPS": """VMs from cloud enterprise""",'CloudCache': """Online course management website; Web server for a CS department user web-
    pages """, 'MSR': """User home directories; Hardware monitoring; Source control; Project directories; Research projects; Web staging; Source control"""}

    for distinct_val in algruns.find().distinct('dataset'):
            datasets.append(distinct_val)
    for key in descriptions:
        db.workload.update_many({'dataset': key}, {'$set': {'description': descriptions[key] }})
        #db.test.update_many({'x': 1}, {'$inc': {'x': 3}})
    #print(current_vals)

if __name__ == "__main__":
    #print(find_in_collection('workload', param=['dataset', 'FIU']))
    #update_desc()
    #heat_map_test()
    '''a = ['algorithm', 'cache_size', 'dataset']
    for i in a:
        update_collection(i)'''
    #update_cache_sizes()
    #update_algs()
    #del_all()
    #update_arch_traces()
    #heat_map_test()
    #update_arch_traces()
    #heat_map_find(['arc'], [0.001], ['FIU'])
    #heat_map_wipe()
    #heat_map_test()
    #del_config()
    '''t1 = time.perf_counter()
    lookup("C:/Users/cyan/python_projects/homes-sample.blkparselecar43")
    t2 = time.perf_counter()
    print(f"Time elapsed to find in storage: {t2 - t1:0.08f} sec.")
    client.close()'''


#delete_workload({'trace name': './homes-sample.blkparse'})
#delete_workload({'trace name': './WorkSpace_nexus5-sample.txt'})

#delete_trace_runs({'hit rate array uploaded to minio': {'$ne':False} })

#delete({'trace name': './home1-sample.blkparse'})


