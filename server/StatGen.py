from lib.traces import identify_trace, get_trace_reader
from lib.progress_bar import ProgressBar
from algs.get_algorithm import get_algorithm
from timeit import timeit
from itertools import product
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import sys
import json
import math
import time
import Minio_Module
import storage
import filereader as fr
import server_utils as serv
import sftp_r
import sf_filereader
import pretty
import conduit

# storage needs 'pymongo[svr]' to work: pip install pymongo[svr]

cwd = os.getcwd()
save_path = cwd + '/output/'
progress_bar_size = 30


def parseConfig(config, algname):
    #print("in parseconfig")
    alg_config = {}
    #print(config)
    if algname in config:
        #print( algname + " CURRENT ALGORITHM ====================================================")
        keywords = list(config[algname])

        #print(str(keywords) + " ----------------------------------------------------- ")
        #print(str(config[algname].values()) + " ******************** config algorithm values")
        for values in product(*config[algname].values()):
            for key, value in zip(keywords, values):
                alg_config[key] = value
                #print(str(alg_config) + " IN GENERATE ALGORITHM TEST" + '\r\n' + '\r\n')
        #return alg_config
        return alg_config
    else:
        return alg_config


#generates a sliding average array from given data.
def slide_avg(array, window):
    temp = np.append(np.zeros(window), array[:-window])
    slide_average = ((array-temp) / window)*100
    return slide_average


# readerLoop: main loop for generating data, calls the reader to run the algorithm and get output data.
# input: reader, algorithm name, hit percentage, miss rate, pollution over time. these are all empty arrays
#
#  
# output: returns result arrays which are
#         miss rate, hit rate, and pollution, the others come back as None unless the correct algorithm is specified.

sftp_data = {}

def readerLoop(reader, alg, hitPerc, missRate, polOT, algname, lba_map, trace_requests):

    #dlirs_HIR_s = []
    #arc_p = []
    #cacheus_learning_rate = []
    #cacheus_lru = []
    #cacheus_q = []
    #lecar_lru = []

    #tracked_params = [dlirs_HIR_s, arc_p, cacheus_learning_rate, cacheus_lru, cacheus_q, lecar_lru]

    special_alg_array = {'dlirs_HIR_s': [], 'arc_p': [],'cacheus_learning_rate': [],'cacheus_lru': [],'cacheus_q': [],'lecar_lru': []}


    count = 0
    misses = 0
    ios = 1

    all_evictions = 0
    evRate = [] # total number of evictions @ point in time
    evictions = [] # number of evictions per requested LBA -SH

    #get sliding window size
    sliding_window = math.floor(0.01*trace_requests)

    print("CURRENT SLIDING WINDOW SIZE ", sliding_window, "============================================")

    if algname.lower() == 'dlirs':
        for items in special_alg_array:
            if 'dlirs' not in items:
                special_alg_array[items] = None

    elif algname.lower() == 'arc':
        for items in special_alg_array:
            if 'arc' not in items:
                special_alg_array[items] = None

    elif algname.lower() == 'cacheus':
        for items in special_alg_array:
            if 'cacheus' not in items:
                special_alg_array[items] = None

    elif algname.lower() == 'lecar':
        for items in special_alg_array:
            if 'lecar' not in items:
                special_alg_array[items] = None
    else:
        for items in special_alg_array:
                special_alg_array[items] = None
    print(algname + "-------------------------------------------------------")

    for lba in reader.read_all():
    
        if lba not in lba_map.keys():
            lba_map[lba] = count
            #evictions.append(0)
        count += 1
        #window_request += 1 
        #window_miss += 1   
        # request(lba) does not return eviction data 
        #print(lba,"lba") 
        miss = alg.request(lba) 
        if miss:
            misses +=1
            #window_miss += 1

        if algname.lower() == 'dlirs':
            current_hir_size = alg.get_hir_size()    
            #print(special_alg_array['dlirs_HIR_s'])
            special_alg_array['dlirs_HIR_s'].append(current_hir_size)

        if algname.lower() == 'arc':
            current_p_value = alg.get_p()
            special_alg_array['arc_p'].append(current_p_value)

        if algname.lower() == 'cacheus':
            current_w_lru_value = alg.get_w_lru()
            current_learning_rate = alg.get_learning_rate()
            current_q_size = alg.get_q()

            special_alg_array['cacheus_lru'].append(current_w_lru_value)
            special_alg_array['cacheus_learning_rate'].append(current_learning_rate)
            special_alg_array['cacheus_q'].append(current_q_size)

        if algname.lower() == 'lecar':
            current_w_lru_value = alg.get_w_lru()
            special_alg_array['lecar_lru'].append(current_w_lru_value)

        #Old way , no sliding window
        ios = reader.requests
        curHit = ios - misses
        hitPerc.append(curHit)
        evRate.append(round(100 * all_evictions/ios, 2)) # eviction rate @ point in time -SH
        #missRate.append(100 - round(100 * curHit/ios, 2))
        missRate.append(misses)
        polOT.append(np.mean(alg.pollution.Y))

        '''if count == trace_requests:
            print("END OF DATA REACHED")
            current_hits = window_request - window_miss
            #print(current_hits)
            hitPerc.append(round(100 * (current_hits/window_request), 2) )

            if window_request == sliding_window:
            current_hits = window_request - window_miss
            #print(current_hits)
            #print(window_request)
            #print(window_miss)
            hitPerc.append(round(100 * (current_hits/window_request), 2) )
            #miss = 0
            window_request = 0
            window_miss = 0'''

    hitPerc = slide_avg(hitPerc, sliding_window)
    missRate = slide_avg(missRate, sliding_window)

    return ios, misses, hitPerc, missRate, polOT, special_alg_array['dlirs_HIR_s'], special_alg_array['arc_p'], special_alg_array['cacheus_learning_rate'], special_alg_array['cacheus_lru'], special_alg_array['cacheus_q'], special_alg_array['lecar_lru']


def testAlgStats(algname, cache_size, config, trace_name):
    print("in get alg stats")

    #alg = get_algorithm(algname)(cache_size, **self.alg_args)
    alg_args = parseConfig(config, algname)
    avg_pollution = 0
    misses = 0
    ios = 1

    #general alg data
    lba_map = {}
    hitPerc = [] #percentage of hits over time
    missRate = [] #miss rate over time
    timestamps = []
    count = 0
    evict = 0
    polOT = [] #pollution over time
    
    #special alg data: depending on which algorithm is called, other information is collected as the algorithm is run 
    dlirs_HIR_s = []

    lecar_lru = []

    arc_p = []

    cacheus_learning_rate =[]
    cacheus_lru = []
    cacheus_q = []

    #   ------------ plot for hit rate over learning rate
    lecarLR = -1 # for any lecar w. fixed learning rate
    
    # evictions data
    all_evictions = 0
    evRate = [] # total number of evictions @ point in time
    evictions = [] # number of evictions per requested LBA -SH


    #trace_type = identify_trace(trace_name)
    #trace_reader = get_trace_reader(trace_type)

    # this is new ----------
    reader = fr.identify_trace(trace_name)

    alg = get_algorithm(algname)(cache_size, **alg_args)

    timestamps.append(0) #time
    init_timestamp = time.perf_counter()

    trace = storage.find_trace(trace_name)
    trace_requests = trace.get("requests")

    ios, misses, hitPerc, missRate, polOT, dlirs_HIR_s, arc_p, cacheus_learning_rate, cacheus_lru, cacheus_q, lecar_lru = readerLoop(reader, alg, hitPerc, missRate, polOT, algname, lba_map, trace_requests)



    lecarLR = alg.learning_rate if algname.lower() == 'lecar' else -1


    avg_pollution = np.mean(alg.pollution.Y)
    ios = reader.requests

    hits = ios - misses

    hitRate = round(100 * (hits / ios), 2)

    finalEvictionR = round(100 * (all_evictions/ios) ) #final eviction rate
    finalEvictionT = len(evictions)

    print(
            "\nResults: {:<10} size={:<8} hits={}, ios = {}, misses={}, hitrate={:4}% avg_pollution={:4}% {}"
            .format(algname, cache_size, hits, ios, misses,
                    hitRate, round(avg_pollution, 2),
                    trace_name, *alg_args.items()))

# getAlgStats: generates statistics for current algorithm, cache size, trace name combination
# input: algorithm name, cache size, config, trace name
# example input: getAlgStats('arc', .2, config, 'homes-sample.blkparse')
# 
# output: prints result data that goes to mongo. sends that data to mongo and minio, returns -1 or the id generated by mongo

def getAlgStats(algname, cache_size, config, trace_name, app_id = None, minio_only = False):
    print("in get alg stats")
    print("==============================================")
    #alg = get_algorithm(algname)(cache_size, **self.alg_args)
    alg_args = parseConfig(config, algname)
    avg_pollution = 0
    misses = 0
    ios = 1

    #general alg data
    lba_map = {}
    hitPerc = [] #percentage of hits over time
    missRate = [] #miss rate over time
    timestamps = []
    count = 0
    evict = 0
    polOT = [] #pollution over time
    
    #special alg data: depending on which algorithm is called, other information is collected as the algorithm is run 
    dlirs_HIR_s = []

    lecar_lru = []

    arc_p = []

    cacheus_learning_rate =[]
    cacheus_lru = []
    cacheus_q = []

    #   ------------ plot for hit rate over learning rate
    lecarLR = -1 # for any lecar w. fixed learning rate
    
    # evictions data
    all_evictions = 0
    evRate = [] # total number of evictions @ point in time
    evictions = [] # number of evictions per requested LBA -SH


    #trace_type = identify_trace(trace_name)
    #trace_reader = get_trace_reader(trace_type)
    if app_id != None:
        conduit.current_status[app_id] = "getting data from sftp server..."
    if sftp_data.get(trace_name) == None:
        print("getting data from sftp server...")
        filename, trace_data = sftp_r.direct_query(trace_name)
        sftp_data[trace_name] = [filename, trace_data]
        print("finished getting data from sftp server...")
        print(filename)
    else:
        filename = sftp_data[trace_name][0]
        trace_data = sftp_data[trace_name][1]
        pretty.success("*\n*\n*\n*\n*\n*\n*\nREUSE")

    print("getting data from sftp server...")
    filename, trace_data = sftp_r.direct_query(trace_name)
    print("finished getting data from sftp server...")

    # this is new ----------
    reader = sf_filereader.identify_trace(filename, trace_data)

    print(filename, " ***************************** ********************** ")
    print(algname)

    alg = get_algorithm(algname)(cache_size, **alg_args)

    print(alg)

    timestamps.append(0) #time
    init_timestamp = time.perf_counter()

    trace = storage.find_trace(trace_name)
    trace_requests = trace.get("requests")
    if app_id != None:
        conduit.current_status[app_id] = "processing " + trace_name + algname + str(cache_size) + " this can take over 10 minutes..."

    ios, misses, hitPerc, missRate, polOT, dlirs_HIR_s, arc_p, cacheus_learning_rate, cacheus_lru, cacheus_q, lecar_lru = readerLoop(reader, alg, hitPerc, missRate, polOT, algname, lba_map, trace_requests)



    lecarLR = alg.learning_rate if algname.lower() == 'lecar' else -1


    avg_pollution = np.mean(alg.pollution.Y)
    ios = reader.requests

    hits = ios - misses

    hitRate = round(100 * (hits / ios), 2)

    finalEvictionR = round(100 * (all_evictions/ios) ) #final eviction rate
    finalEvictionT = len(evictions)

    print(
            "\nResults: {:<10} size={:<8} hits={}, ios = {}, misses={}, hitrate={:4}% avg_pollution={:4}% {}"
            .format(algname, cache_size, hits, ios, misses,
                    hitRate, round(avg_pollution, 2),
                    trace_name, *alg_args.items()))
    print(dlirs_HIR_s, lecar_lru, arc_p, cacheus_learning_rate, cacheus_lru, cacheus_q)
    mongo_trace_runs_id = serv.as_to_Database(trace_name, algname, cache_size, ios, hits, hitRate, misses, round(avg_pollution, 2) , finalEvictionR, finalEvictionT, 
                    hitPerc, missRate, polOT, minio_only, dlirs_HIR_s, lecar_lru, arc_p, cacheus_learning_rate, cacheus_lru, cacheus_q)
    if app_id != None:
        conduit.current_status[app_id] = "processing " + trace_name + algname + str(cache_size) + " complete"

    print("---------------------MONGO TRACE RUNS ID BEING SENT TO CONFIRM", mongo_trace_runs_id)
    #if not minio_only:
    confirmed = serv.as_minio_confirm(mongo_trace_runs_id, trace_name, algname, cache_size)

    if confirmed:
        return mongo_trace_runs_id
    else:
        return -1



def generateTraceNames(trace):
    """
    Generate all the trace file inside a directory.

    Parameters
    ----------
    trace: relative path to the folder or a file trace 
    """
    #print("generate trace names called")
    #print(trace)
    if trace.startswith('~'):
        trace = os.path.expanduser(trace)

    if os.path.isdir(trace):
        for trace_name in os.listdir(trace):
            yield os.path.join(trace, trace_name)
    elif os.path.isfile(trace):
        yield trace
    else:
        raise ValueError("{} is not a directory or a file".format(trace))


# singleTraceGen: generates the statistics for a given trace and uploads data to mongo and minio 
# input: trace name
# input example: singleTraceGen('homes-sample.blkparse')
# output: outputs mongo trace ID. this is needed to confirm with minio that the data was in fact uploaded correctly.
# output example: '5eb2a7f95ef07cbca3668020'

#there is an optional argument placed here for the case where the data is already in MongoDB but there is no graph data in Minio.

def singleTraceGen(trace, minio_only = False):
    print("IN SINGLE TRACE GEN")

    print(trace)

    traces = generateTraceNames(trace)
    #traces = trace
    print(trace)

    traceplot = {}

    for trace in traces:
        print('single trace gen:')
        print("\nTRACE NAME ================================== " + trace)


        print("getting data from sftp server...")
        trace_name, trace_data = sftp_r.direct_query(trace)
        print("finished getting data from sftp server...")
        # this is new ----------
        reader = sf_filereader.identify_trace(trace_name, trace_data)

        print("in single trace gen")

        count = 0
        accesses = {}
        req = []
        num = 0
        #keys in this dicitonary are the sanitized LBAs and the values are number of access
        reqFreq = [] 
        histogram = {}
        reuse_distance = {}
        timestamps = []


        max_accesses = 0

        max_reused = 0
        
        #reuse_distance is a list of lists where the key is the lba and the value is the list of when that lba is called.
        #we use this list later on to calculate reuse distance frequency distribution.
        for lba in reader.read_all(): # instead of reader.read()
            count += 1
            if lba not in accesses.keys():
                accesses[lba] = num
                reqFreq.append(0) #now a list
                num +=1
                reuse_distance[accesses[lba]] = [count]
            else:
                reuse_distance[accesses[lba]].append(count) 


            #we are checking for max reused to determine the size of the resulting array
            req.append(accesses[lba])
            reqFreq[accesses[lba]] += 1
            times_accessed = reqFreq[accesses[lba]]
            if max_reused < len(reuse_distance[accesses[lba]]):
                max_reused = len(reuse_distance[accesses[lba]])

            #this tells us upper bound for access frequency's x axis
            if times_accessed > max_accesses:
                max_accesses = times_accessed

            #the keys in histogram are the number of times a reuse distance has been counted
            #the reqFreq array keeps track of individual LBAs and how many times they have been called so far
            if histogram.get(times_accessed) == None:
                histogram[times_accessed] = 1
            else:
                histogram[times_accessed] += 1
                if times_accessed > 1:
                    histogram[times_accessed - 1] -= 1

        histogram[0] = max_accesses

        reuse_distance['max_reused'] = max_reused


        entry = {}


        curdata = { 
                    'number of requests': reader.requests, 
                    'number of unique requests': reader.uniques,
                    'number of reuses': reader.reuses,
                    'number of writes': reader.writes,
                    'time': reader.requests,
                  }

        entry[trace] = curdata
        #print(str(curdata)) # ============================================ writes check - remove


        #requestFrequencyOutput = trace + "_REQUEST_FREQ"  
        #requestsOutput = trace + "_REQUEST"

        #np.savez_compressed(requestFrequencyOutput, reqFreq)
        #np.savez_compressed(requestsOutput, req)
        
        # np.savez_compressed(trace, req, regFreq, misses, hitPerc, ios, polOT, missRate)


        print("TRACE NAME ------------------------- :", trace)

       
        #this is where the data gets sent to mongodb
        mongo_trace_id = serv.s_to_database(trace, reader.requests, reader.uniques, reader.reuses, reader.writes, 
                        reader.requests, req, histogram, reuse_distance, reader.time_stamp, minio_only)
        mongo_trace_id = str(storage.find_id(trace))
        confirmed = serv.s_minio_confirm(mongo_trace_id, trace)
        '''if os.path.exists(traceOutput) == False:
            with open(traceOutput, 'a+') as f:
                final = json.dumps(entry, indent=4, sort_keys=True,
                    separators=(',', ': '), ensure_ascii=False)
                f.write(final)
        else:
            with open(traceOutput) as f:
                data = json.load(f)

            data.update(entry)

            with open(traceOutput, 'w') as f:
                final = json.dumps(data, indent=4, sort_keys=True,
                    separators=(',', ': '), ensure_ascii=False)
                f.write(final)'''
        if confirmed:
            return mongo_trace_id
        else:
            return False
print("StatGen active", time.time())


def sf_singleTraceGen(trace, app_id = None,  minio_only = False):
    print("IN SINGLE TRACE GEN")

    print(trace)

    #traces = generateTraceNames(trace)
    traces = trace
    print(trace)

    traceplot = {}

   
    print('single trace gen:')
    print("\nTRACE NAME ================================== " + trace)
    if app_id != None:
        conduit.current_status[app_id] = "getting "  + trace + ' from sftp server... please wait'
    if sftp_data.get(trace) == None:
        print("getting data from sftp server...")
        filename, trace_data = sftp_r.direct_query(trace)
        sftp_data[trace] = [filename, trace_data]
        print("finished getting data from sftp server...")
        print(filename)
    else:
        filename = sftp_data[trace][0]
        trace_data = sftp_data[trace][1]
        pretty.success("*\n*\n*\n*\n*\n*\n*\nREUSE")


    if app_id != None:
        conduit.current_status[app_id] = 'Processing trace data for ' + trace + '... please wait this can take over 10 minutes'

    # this is new ----------
    reader = sf_filereader.identify_trace(filename, trace_data)


    count = 0
    accesses = {}
    req = []
    num = 0
    #keys in this dicitonary are the sanitized LBAs and the values are number of access
    reqFreq = [] 
    histogram = {}
    reuse_distance = {}
    timestamps = []


    max_accesses = 0

    max_reused = 0
        
    #reuse_distance is a list of lists where the key is the lba and the value is the list of when that lba is called.
    #we use this list later on to calculate reuse distance frequency distribution.
    for lba in reader.read_all(): # instead of reader.read()
        count += 1
        if lba not in accesses.keys():
            accesses[lba] = num
            reqFreq.append(0) #now a list
            num +=1
            reuse_distance[accesses[lba]] = [count]
        else:
            reuse_distance[accesses[lba]].append(count) 


        #we are checking for max reused to determine the size of the resulting array
        req.append(accesses[lba])
        reqFreq[accesses[lba]] += 1
        times_accessed = reqFreq[accesses[lba]]
        if max_reused < len(reuse_distance[accesses[lba]]):
            max_reused = len(reuse_distance[accesses[lba]])

        #this tells us upper bound for access frequency's x axis
        if times_accessed > max_accesses:
            max_accesses = times_accessed

        #the keys in histogram are the number of times a reuse distance has been counted
        #the reqFreq array keeps track of individual LBAs and how many times they have been called so far
        if histogram.get(times_accessed) == None:
            histogram[times_accessed] = 1
        else:
            histogram[times_accessed] += 1
            if times_accessed > 1:
                histogram[times_accessed - 1] -= 1

    histogram[0] = max_accesses

    reuse_distance['max_reused'] = max_reused


    entry = {}


    curdata = { 
                'number of requests': reader.requests, 
                'number of unique requests': reader.uniques,
                'number of reuses': reader.reuses,
                'number of writes': reader.writes,
                'time': reader.requests,
                }

    entry[trace] = curdata
        #print(str(curdata)) # ============================================ writes check - remove


        #requestFrequencyOutput = trace + "_REQUEST_FREQ"  
        #requestsOutput = trace + "_REQUEST"

        #np.savez_compressed(requestFrequencyOutput, reqFreq)
        #np.savez_compressed(requestsOutput, req)
        
        # np.savez_compressed(trace, req, regFreq, misses, hitPerc, ios, polOT, missRate)


    print("TRACE NAME ------------------------- :", trace)
    if app_id != None:
        conduit.current_status[app_id] =  trace + ' data processed, uploading to server... please wait'
       
    #this is where the data gets sent to mongodb
    mongo_trace_id = serv.s_to_database(trace, reader.requests, reader.uniques, reader.reuses, reader.writes, 
                    reader.requests, req, histogram, reuse_distance, reader.time_stamp, minio_only)
    mongo_trace_id = str(storage.find_id(trace))
    confirmed = serv.s_minio_confirm(mongo_trace_id, trace)

    if confirmed:
        return mongo_trace_id
    else:
        return False

