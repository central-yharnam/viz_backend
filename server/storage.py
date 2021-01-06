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
with open(os.environ['MONGO_CLIENT']) as f:
    entry = f.read()
client = MongoClient(entry)
db = client.get_database('cache_trace')


#store data for one workload
def store_workload(name, total, unique, reuses, writes, time):
    traces = db.workload
    new_trace = {
        'trace name' : name,
        'requests' : total,
        'unique' : unique,
        'reuses' : reuses,
        'writes' : writes,
        'time' : time,
        'requests uploaded to minio': False,
        'request frequency uploaded to minio' : False
    }
    traces.insert_one(new_trace)

def workload_confirmed(traceName, request = None, requestFrequency = None, reuseDistance = None, time = None):
    pretty.utility("CONFIRMING THAT" +  traceName + "DATA WAS UPLOADED TO MINIO")
    traces = db.workload
    if request != None:
        pretty.success("REQUEST ARRAY CONFIRMED UPLOADED TO MINIO")
        traces.update_one({'trace name': traceName}, {'$set':{'requests uploaded to minio': datetime.now()}})

    if requestFrequency != None: 
        pretty.success("REQUEST FREQUENCY ARRAY CONFIRMED UPLOADED TO MINIO")
        traces.update_one({'trace name': traceName}, {'$set':{'request frequency uploaded to minio': datetime.now()}})

    if reuseDistance != None: 
        pretty.success("REUSE DISTANCE ARRAY CONFIRMED UPLOADED TO MINIO")
        traces.update_one({'trace name': traceName}, {'$set':{'reuse distance uploaded to minio': datetime.now()}})

    if time != None: 
        pretty.success("REAL TIME ARRAY CONFIRMED UPLOADED TO MINIO")
        traces.update_one({'trace name': traceName}, {'$set':{'REAL TIME uploaded to minio': datetime.now()}})

def trace_run_confirmed(traceId, hit_rate = None, miss_rate = None, pollution = None, dlirs = None, lecar = None, arc = None, cacheus = None):
    #print("IN TRACE RUN CONFIRM METHOD")
    alg_stats = db.trace_runs
    pretty.utility("CONFIRMING THAT ALGORITHM DATA WAS UPLOADED TO MINIO")
    print(traceId)

    if hit_rate != None:
        pretty.success("HIT RATE ARRAY CONFIRMED UPLOADED TO MINIO")
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'hit rate array uploaded to minio': datetime.now()}})

    if miss_rate != None:
        pretty.success("MISS RATE ARRAY CONFIRMED UPLOADED TO MINIO")
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'miss rate array uploaded to minio': datetime.now()}})

    if pollution != None:
        pretty.success("POLLUTION ARRAY CONFIRMED UPLOADED TO MINIO")
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'pollution array uploaded to minio': datetime.now()}})

    if dlirs != None:
        pretty.success("DLIRS STACK ARRAY CONFIRMED UPLOADED TO MINIO")
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'dlirs stack array uploaded to minio': datetime.now()}})

    if lecar != None:
        pretty.success("LECAR LRU SIZE ARRAY CONFIRMED UPLOADED TO MINIO")
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'lecar lru size array uploaded to minio': datetime.now()}})

    if arc != None:
        pretty.success("ARC P VALUE ARRAY CONFIRMED UPLOADED TO MINIO")
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'arc p size array uploaded to minio': datetime.now()}})

    if cacheus != None:
        pretty.success("CACHEUS LEARNING RATE, LRU VALUE AND Q VALUE CONFIRMED UPLOADED TO MINIO")
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'cacheus learning rate array uploaded to minio': datetime.now()}})
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'cacheus lru size array uploaded to minio': datetime.now()}})
        alg_stats.update_one({'_id': ObjectId(traceId)}, {'$set':{'cacheus q value array uploaded to minio': datetime.now()}})

# store data for one algorithm
# trace run result with reference to algorithm specs object
# find_one({'_id' : ObjectId('5e3a2c8a1c9d4400006505c0')})
def store_alg(hitp, missr, polOT, evRate, evcs, alg_name, cache_size, t_name):
    alg_specs = db.algorithm_specs
    new_algorithm = {
        'algorithm': alg_name,
        'cache size': cache_size
    }
    alg_object = alg_specs.insert_one(new_algorithm)
    workload_data = find_trace(t_name)

    runs = db.trace_runs
    trace_data = {}
    trace_data['algorithm specs'] = alg_object.inserted_id
    trace_data['trace'] = find_trace(t_name)["_id"]
    trace_data['date'] = datetime.now()

    # new_trace = { trace_data }
    runs.insert_one(trace_data)

# store data for one algorithm
# trace run result with reference to algorithm specs object
# find_one({'_id' : ObjectId('5e3a2c8a1c9d4400006505c0')})
'''
   Same structure as before but now the arguments given send single value integers 
   generated by getAlgStats. furthermore the collection is flattened: algorithm 
   and cache size are fields in trace_runs rather than a seperate collection
'''

def new_store_alg(ios, hits, hit_rate, misses, pollution, evRate, evcs, alg_name, cache_size, t_name):
    print("IN NEW STORE ALG METHOD")
    runs = db.trace_runs
    trace_data = {}
    trace_data['trace'] = find_trace(t_name).get("_id")
    trace_data['algorithm'] = alg_name
    trace_data['cache_size'] = cache_size
    trace_data['date'] = datetime.now()
    trace_data['ios'] = ios
    trace_data['total hits'] = hits
    trace_data['final hit rate'] = hit_rate
    trace_data['final misses'] = misses
    trace_data['final pollution'] = pollution
    trace_data['hit rate array uploaded to minio'] = False
    trace_data['miss rate array uploaded to minio'] = False
    trace_data['pollution array uploaded to minio'] = False

    if alg_name == 'dlirs':
        trace_data['dlirs stack array uploaded to minio'] = False
    if alg_name == 'lecar':
        trace_data['lecar lru size array uploaded to minio'] = False
    if alg_name == 'arc':
        trace_data['arc p size array uploaded to minio'] = False
    if alg_name == 'cacheus':
        trace_data['cacheus learning rate array uploaded to minio'] = False
        trace_data['cacheus lru size array uploaded to minio'] = False
        trace_data['cacheus q value array uploaded to minio'] = False

   # new_trace = { trace_data }
    runs.insert_one(trace_data)


# inserts config file to a config collection, to be displayed by website
# a list of the basenames of the files in the config is generated and pushed to the database so that when the config is accessed 
# by the database and queried later, it tries to find just the file name rather than the local filepath provided by the config.
#
# return id of inserted object
def insert_config(config, name):
    print("IN INSERT CONFIG")
    conf = db.configs
    conf_obj = conf.find_one({'name': name})
    ins =''
    all_traces = []
    if conf_obj == None:
        for traces in set(config['traces']):
            for trace_names in StatGen.generateTraceNames(traces):
               all_traces.append(os.path.basename(trace_names))  
               print(os.path.basename(trace_names))   
        # got an error saying a set cannot be encoded by json so I make it a set and then a list again. 
        # The reason it is cast as a set is to remove duplicates in a simple manner 
        all_traces = set(all_traces)
        all_traces =  list(all_traces)
        config['traces'] = all_traces
        config["name"] = name
    ins = str(conf.insert_one(config).inserted_id)
    return ins



'''def remove_config(name):
    conf = db.configs
    conf.delete_one({'name':name})'''

'''def remove_all_configs():
    for conf in get_all_configs():
        print("removing all configs")
        remove_config(conf.get("name"))'''


def get_all_configs():
    all_configs = db.configs
    configs = all_configs.find()
    for c in configs:
        yield c
#returns all MongoDB data for config with a given id
def find_config(c_id):
    all_configs = db.configs
    json_cfg = json.dumps(
        all_configs.find_one({"_id": ObjectId(str(c_id))}), default=json_util.default, indent=4)
    #config = all_configs.find_one({"_id": c_id})
    return json_cfg


#search for a previously run trace
#key is the key corresponding to the trace name in the workload collection combined with which algorithm and cache size is used
#returns the alg stat object in the mongdb collection of trace-algorithm-cache_size in trace_runs collection

def find_trace_run(trace_name, algorithm, cache_size):
    runs = db.trace_runs
    workloads = db.workload

    workload_obj = workloads.find_one({'trace name': trace_name})

    if workload_obj == None:
        print("trace not found")
        return False

    trace_run_id = workload_obj.get("_id")
    currentTrace = runs.find_one({'trace': trace_run_id, 'algorithm': algorithm, 'cache_size': cache_size})

    if currentTrace == None:
        print("Error, trace not found")
        return False

    return currentTrace

    #iden = str(currentTrace.get("_id"))
    #return iden

# there are special graphs that are only valid for specific algorithms, 
# so it is necessary to generate a list with all traces run with a given algorithm for graphing
'''def find_alg_trace_run(trace_name, algorithm):
    runs = db.trace_runs
    workloads = db.workload

    workload_obj = workloads.find_one({'trace name': trace_name})

    if workload_obj == None:
        print("trace not found")
        return False

    trace_run_id = workload_obj.get("_id")
    currentTrace = runs.find({'trace': trace_run_id, 'algorithm': algorithm})

    if currentTrace == None:
        print("no trace runs found with algorithm ", algorithm)

    return currentTrace'''


#pass the filename of a csv file and check if it is in the database
def find_csv_run(csv_filename):
    rank = db.rank_csv
    csv_obj = rank.find_one({'name': os.path.basename(csv_filename)})
    if csv_obj == None:
        pretty.failure("csv object not found")
        return False
    return csv_obj

#check if a csv file is already in database and insert if it is not
'''def insert_csv_run(csv_filename):
    pretty.utility("inserting csv data")
    rank = db.rank_csv
    #csv_obj = rank.find_one({'name': csv_filename})
    
    csv_obj = rank.find_one({'name': os.path.basename(csv_filename)})
    if csv_obj == None:
        rank_meta = {}
        rank_meta['name'] = csv_filename
        rank.insert_one(rank_meta)
        pretty.utility("verifying " + csv_filename + " upload")
        csv_obj = rank.find_one({'name': os.path.basename(csv_filename)})
        if csv_obj != None:
            pretty.success(csv_filename + " successfully uploaded")
            return True
        else:
            pretty.failure(csv_filename + " upload failed")
            return False
    else:
        pretty.success(csv_filename + " already in database") 
        return True'''
            


#return all -as results from a particular trace for plotting purposes
'''def find_all_trace_runs(trace_name):
    runs = db.trace_runs
    workloads = db.workload

    workload_obj = workloads.find_one({'trace name': trace_name})

    if workload_obj == None:
        print("trace not found")
        return False

    trace_run_id = workload_obj.get("_id")
    currentTrace = runs.find({'trace': trace_run_id})

    if currentTrace == None:
        print("Error, trace not found")
        return False

    return currentTrace'''

#return the ID of the results of a certain trace name, algorithm, cache size combination

def find_trace_run_id(trace_name, algorithm, cache_size):
    runs = db.trace_runs
    workloads = db.workload

    workload_obj = workloads.find_one({'trace name': trace_name})


    if workload_obj == None:
        print("trace not found")
        return False

    trace_run_id = workload_obj.get("_id")
    currentTrace = runs.find_one({'trace': trace_run_id, 'algorithm': algorithm, 'cache_size': cache_size})

    if currentTrace == None:
        print("Error, trace not found")
        return False

    iden = str(currentTrace.get("_id"))
    return iden

# workload trace lookup by trace name, return all data fields for that trace name
def find_trace(trace_name):
    workloads = db.workload
    currentTrace = workloads.find_one({'trace name' : trace_name})
    if (currentTrace == None):
        pretty.failure("trace not found")
        return False
    else:
        return currentTrace
        
# isnt used 
# return the algorithm specs for a given algorithm
'''def find_algo(alg_name):
    algos = db.algorithm_specs
    return algos.find_one({'algorithm' : alg_name})'''


# find Mongo ObjectID of object with a given trace name.
def find_id(trace_name):
    workloads = db.workload
    currentTrace = workloads.find_one({'trace name' : trace_name})
    print(currentTrace)
    if currentTrace == None:
        pretty.failure("Trace not found")
        return False
    iden = str(currentTrace.get("_id"))
    #print(iden)
    return iden

# pass a collection to the function and find everything with your given parameter, if param is None it will return everything in the collection.
# returns a list
# param is a list. param[0] is the field you want to search on and param[1] is the value you want to search for 
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
    retty.utility("deleting plots with param: ", param)
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


