from lib.traces import identify_trace, get_trace_reader
from lib.progress_bar import ProgressBar
from algs.get_algorithm import get_algorithm
from timeit import timeit
from itertools import product
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import json
import visual.StatVis as sv
import StatGen as sg
import storage
import Minio_Module
import math
import pretty
import pandas as pd
import time 
import conduit
import tempfile

#import storage as stor

##########################
# These are the methods used to contact mongo and minio
#########################


# the loop structure for all of these methods is almost identical
# go through all traces in the config file, if algorithm data is being generated, calculate cache size and iterate through all algorithms.
#
# generateTraceNames goes through the directory and generates a list of all valid files
# generateTraceNames is necessary because it is possible to pass a directory in the 'traces' field in the config.
#


# mongo_new_paths: makes a query to mongo for all workload traces in the config file passed as an argument
# input: config file that has been loaded into memory
# output: a list of new traces

def mongo_new_paths(config):
    pretty.utility("CONTACTING MONGODB... CHECKING FOR NEW PATHS")
    newTraces = []
    for traces in config['traces']:
        for trace_name in sg.generateTraceNames(traces):
            mongo_trace = storage.find_trace(trace_name)
            if mongo_trace == False:
                newTraces.append(trace_name)
            else: 
                pretty.success("Trace: " + mongo_trace["trace name"])
                pretty.success("Total number of requests: " + str(mongo_trace['requests']))
                pretty.success("Total number of unique requests: " + str(mongo_trace['unique']) )
                pretty.success("Total number of reuses: " + str(mongo_trace['reuses']) )
                pretty.success("Total number of writes: " + str(mongo_trace['writes']) )
                pretty.success("Total time: " + str(mongo_trace['time']) )
                pretty.success('\n')
    return newTraces



# printMongoResults: makes a query to mongo for a trace and prints results if found
# input: trace name
# example input: printMongoResults("homes-sample.blkparse")
# output: trace data

def printMongoResults(trace_name):
    pretty.utility("retrieving previous results from MongoDB...")
    trace_result = storage.find_trace(trace_name)
    if trace_result != False:
        print("trace name: ", trace_result['trace name'])
        print("requests: ", trace_result['requests'])
        print("unique: ", trace_result['unique'])
        print("reuses: ", trace_result['reuses'])
        print("writes: ", trace_result['writes'])
        print("time: ", trace_result['time'])
    else:
        print(trace_name, "not found")

# mongo_new_alg_runs: makes a query to mongo for all algorithms and cache sizes in config 
# input: config file that has been loaded into memory
# output: if the trace is found, the resulting data is printed. if the trace is not found the algorithm and cache size is run 
# 		  then the data is printed 

def mongo_new_alg_runs(config):
    print("sup im in mongo alg new runs")
    print(config)
    for traces in config['traces']:
        for trace_name in sg.generateTraceNames(traces):
            for algorithms in config['algorithms']:
                for cache_size in config['cache_sizes']:
                    cache_size = math.floor(cache_size * mongo_get_unique(trace_name))
                    if cache_size > 10:
                        previously_run = storage.find_trace_run_id(trace_name, algorithms, cache_size)
                        if previously_run == False:
                             confirmed = sg.getAlgStats(algorithms, cache_size, config, trace_name)
                             if confirmed:
                             	trace_run = storage.find_trace_run(trace_name, algorithms, cache_size)
                             	print("===== trace name: ", trace_name, " algorithm:", algorithms, " cache_size", cache_size, " =====")
                             	print("total ios: ", trace_run['ios'])
                             	print("total hits: ", trace_run['total hits'])
                             	print("final hit rate: ", trace_run['final hit rate'])
                             	print("final misses: ", trace_run['final misses'])
                             	print("final pollution: ", trace_run['final pollution'])
                             else:
                             	print("upload to databases failed")
                             	return False
                        else:
                            trace_run = storage.find_trace_run(trace_name, algorithms, cache_size)
                            print("===== trace name: ", trace_name, " algorithm:", algorithms, " cache_size", cache_size, " =====")
                            print("total ios: ", trace_run['ios'])
                            print("total hits: ", trace_run['total hits'])
                            print("final hit rate: ", trace_run['final hit rate'])
                            print("final misses: ", trace_run['final misses'])
                            print("final pollution: ", trace_run['final pollution'])
                            #print("final eviction rate: ", trace_run['final eviction rate'])
                            #print("total evictions: ", trace_run['total evictions'])

# request_alg_run_plot_data: this is a helper method run by "mongo_get_alg_run_plot_data." it requests data corresponding to the 
#							 current combination of trace, algorithm, cache size and plot. 
#
#							A query is sent to mongo for the data of an algorithm run with the currently specified trace name, 
#							algorithm and cache size. If successful, the current algorithm run's mongo data will be loaded into memory.
#							the mongo ID is taken from the mongo data and the desired plot is appended to it and that file ID is sent 
#							to minio so that the correspnding file can be retrieved.
#							
#							 
#							Compressed numpy files in minio are stored as 'minio-id + plot code'. For example, 5eacab1d7471ccfe3ce948ed-rq
#							
#							plot codes are: '-rq' (an array of LBA requests made), -reuse (reuse distance frequencies), 
#											'-histogram' (LBA access frequency distribution), '-hit_rate' (sliding window hit rate data)
#											'-pollution' (pollution data, generated by pollutionator), 
#											'-miss_rate' (same as hit rate except for misses),
#											'-lecar_lru', '-arc_p', '-dlirs_stack', '-cacheus_lru', '-cacheus_learning_rate', '-cacheus_q'
#											(all of these are specific to one algorithm and return an array of the corresponding tracked value
#										    at every request)
#											These can plot flags can also be found in mongodb in a collection called "plots_tracked"
#
# input: trace name, algorithm, cache size, plot, minio module
# example input: request_alg_run_plot_data("homes-sample.blkparse", "arc", .02, '-hit_rate')
# output: minio_get.retrieve, if successful will write a file to disk with the corresponding data and returns the file's name so that 
#		  matploblib can access it. if not, it will return -1.
#
# example output: 'homes-sample.blkparse_43_arc_-hit_rate.npz' this corresponds to the file written to current directory as well.
#
# 		  

def request_alg_run_plot_data(trace_name, algorithm, cache_size, plot, minio_get):
    alg_result = storage.find_trace_run(trace_name, algorithm, cache_size)
    alg_result_id = alg_result.get("_id")
    alg_result_cache_size = alg_result.get("cache_size")
    alg_result_algorithm = alg_result.get("algorithm")

    header = "./graph data/" + trace_name + "_" + str(alg_result_cache_size) + "_" + str(alg_result_algorithm) + "_" + plot + '.npz'

    minio_id = str(alg_result_id) + plot
    #print(minio_id)
    tmp = tempfile.NamedTemporaryFile(suffix='.npz')

    #success = minio_get.retrieve(header, minio_id)
    success = minio_get.retrieve(tmp.name, minio_id)
    if success:
        pretty.success(header + ' downloaded succesfully and ready for plotting')
        file = np.load(tmp.name, allow_pickle = True)
        return file   # tmp.name
    else: 
        pretty.failure("plot data not loaded succesfully")
        return success

# mongo_get_alg_run_plot_data: this method checks if the current combination of trace, algorithm and cache size is in the database.
#							   if it is, it makes a request to minio. if not, it runs the algorithm on the trace with given cache size
#							   and then makes a request for the plot data. 
#								 
#
# input: config, plot, trace name, algorithm, cache size, minio module
#		 (config is necessary every though we're not iterating through everything in the config file here because if the 
#		  requested alg combination is not present we may need to get additional arguments from the config related to the algorithm)
# example input: mongo_get_alg_run_plot_data(config, plot, trace_name, algorithm, cache_size, minio_get)
# output: minio file is written to direction with format "trace name + plot.npz", this name is also returned by the method to the caller.
#
# example output: homes-sample.blkparse-rq.npz is written to directory and this name is also returned by the method


def mongo_get_alg_run_plot_data(config, plot, trace_name, algorithm, cache_size, minio_get, app_id = None):

    minio_get = Minio_Module.Minio_Module()
    graph = sv.StatVis()

    print('in mongo get plot data')


    if app_id != None:
        conduit.current_status[app_id] = "checking if data has been run..."

    '''if os.path.exists(filename):
        pretty.success("file already downloaded to disk")
        if app_id != None:
            conduit.current_status[app_id] = "File already processed and ready, rendering..."
        return filename'''

    previously_run = storage.find_trace_run_id(trace_name, algorithm, cache_size)
    print(previously_run, "previously run?")
    if previously_run == False:

        conduit.current_status[app_id] = "data has not been run before... processing"
        pretty.utility("trace run request: " + trace_name + algorithm + str(cache_size) + " was not found in the database... inserting into database")
        if app_id != None:
            conduit.current_status[app_id] = "trace run request: " + trace_name + " " + algorithm + " " + str(cache_size) + " was not found in the database... processing and inserting into database"
        
        confirmed = sg.getAlgStats(algorithm, cache_size, config, trace_name, app_id)
        if confirmed:
        	out_file = request_alg_run_plot_data(trace_name, algorithm, cache_size, plot, minio_get)
        	return out_file
        else:
        	pretty.failure("upload to database failed")
        	return False
    else:
        conduit.current_status[app_id] = "data has been run before... retrieving data"
        out_file = request_alg_run_plot_data(trace_name, algorithm, cache_size, plot, minio_get)
        return out_file
        


# mongo_get_trace_run_plot_data: this method is for getting trace data from minio.
#								 all that is needed for trace data is the name of the trace and the desired plot. 
#								 if no trace data is found, it is generated.
#
# input: trace name, plot, minio module
# example input: mongo_get_trace_run_plot_data("homes-sample.blkparse", '-rq', minio_module)
# output: minio file is written to direction with format "trace name + plot.npz"
#
# example output: homes-sample.blkparse-rq.npz is written to directory and this name is returned by the method

def mongo_get_trace_run_plot_data(trace_name, plot, minio_get, app_id = None):
    
        '''filename = "./graph data/"+str(trace_name) + str(plot) +'.npz'
        if os.path.exists(filename):
            pretty.success("file already downloaded to disk")
            return filename'''

        print(plot, "********************************")
        print(trace_name)

        trace = storage.find_trace(trace_name)

        if trace == False:
            pretty.utility("plot data for " + trace_name + plot + " was not found, inserting into database...")
            if app_id != None:
                conduit.curret_status[app_id] = "plot data for " + trace_name + " " + plot + " was not found, inserting into database..."
            confirmed = sg.sf_singleTraceGen(trace_name, app_id)
            trace = storage.find_trace(trace_name)
            trace_id = trace.get("_id")
            minio_id = str(trace_id)+plot

            tmp = tempfile.NamedTemporaryFile(suffix='.npz')

            #success = minio_get.retrieve(header, minio_id)
            #success = minio_get.retrieve(tmp.name, minio_id)

            if confirmed:
                success = minio_get.retrieve(tmp.name, minio_id)
                if success:
                    return tmp   # tmp.name
                else:

                    return False
            else:
                pretty.failure("error uploading trace data to database")
                return False
        else:

            trace_id = trace.get("_id")
            trace_ios = trace.get("requests")
            #print("Mongo contacted")
            #print(trace_id, " received id for", trace_name, plot)
            minio_id = str(trace_id)+plot
            
            #print("mongo_get_trace_run_plot_data", minio_id)
            pretty.utility("retrieving plot data from minio...")

            tmp = tempfile.NamedTemporaryFile(mode='w+b', suffix='.npz')

            success = minio_get.retrieve(tmp.name, minio_id)
            if success:
                pretty.success("plot data for " + trace_name + plot + " successfully downloaded")
                #print(filename)
                file = np.load(tmp.name, allow_pickle = True)
                return file    # tmp.name
            else:
                pretty.failure("data not found in minio store... processing trace data...")
                confirmed = sg.sf_singleTraceGen(trace_name, minio_only = True)
                success = minio_get.retrieve(tmp.name, minio_id)
                if success:
                    file = np.load(tmp.name, allow_pickle = True)
                    return file     # tmp.name
                else:
                    print("error uploading data to minio")
                    return False




# normalize_real_time: this method goes through the array of time stamps and takes the difference between them and the starting time to get
#					   time elapsed. 
#								 
#
# input: time stamp array
# example input: normalize_real_time(time_stamps)
# output: outputs a new array with the new timestamps starting at 0
#
# example output: [0, 20, 50 ...]
#

def normalize_real_time(time_stamps):
    
    #print("NORMALIZING REAL TIME")
    normalized_time = []

    zero_time = time_stamps[0]

    for time in time_stamps:
        normalized_time.append(time - zero_time)
    #print(normalized_time)    
    return normalized_time

# get_over_time_list: this method makes a query to mongodb for the id of the requested trace then makes a query to minio for the 
#					  time array with the mongo id. After that it processes the data and returns a timestamp array that starts at 0.
#								 
# input: name of trace
# example input: get_over_time_list(homes-sample.blkparse)
# output: outputs a new array with the new timestamps starting at 0
#
# example output: [0, 20, 50 ...]
#

def get_over_time_list(trace_name, minio_get, app_id = None):
    print("in get over time list")

    '''filename = './graph data/' + trace_name + '_time.npz'
    if os.path.exists(filename):
        pretty.success("file already downloaded to disk")
        data_time = np.load(('./graph data/' + trace_name + '_time.npz'), allow_pickle = True)
        data_time = data_time['arr_0']
        data_time = data_time[()]
        over_time = normalize_real_time(data_time)
        return over_time'''

    trace = storage.find_trace(trace_name)
    print(trace_name)
    print(trace)
    if trace == None:
        print(trace_name, "could not be found in mongodb")
        return False
    else:
        trace_id = trace.get("_id")
        trace_uniques = trace.get("unique")
        pretty.utility("Mongo contacted.. retrieving over time array for " + trace_name)
        #print(trace_name + "===========================")
        #print(trace_id, " received id for", trace_name)

        tmp = tempfile.NamedTemporaryFile(suffix='.npz')

        #real time 
        minio_id_time = str(trace_id)+'-time'
        #res = minio_get.retrieve( ('./graph data/' + trace_name + '_time.npz'), minio_id_time)
        res = minio_get.retrieve(tmp.name, minio_id_time)


        #due to how npz files are compressed, the data must be accessed with a key even if there is only 1 thing in the uncompressed npz file
        #since there is only 1 thing and no name is specified the first thing will always have the name 'arr_0'
        #similarly, the data_time[()] argument is to deal with the 0 dimensional array that is returned. 
        if res:
            #data_time = np.load(('./graph data/' + trace_name + '_time.npz'), allow_pickle = True)
            data_time = np.load(tmp.name, allow_pickle=True)
            data_time = data_time['arr_0']
            data_time = data_time[()]
            over_time = normalize_real_time(data_time)
            pretty.success("Mongo retrieval successful")
            return over_time

        else:
            sg.sf_singleTraceGen(trace_name, app_id,  minio_only = True)
            #result = minio_get.retrieve( ('./graph data/' + trace_name + '_time.npz'), minio_id_time)
            result = minio_get.retrieve(tmp.name, minio_id_time)
            if result:
                data_time = np.load(tmp.name, allow_pickle = True)
                data_time = data_time['arr_0']
                data_time = data_time[()]
                over_time = normalize_real_time(data_time)
                pretty.success("Mongo retrieval successful")
                return over_time
            else:
                return False

# mongo_get_unique: get the number of unique LBAs for a given trace
# input: trace name
# input example: mongo_get_unique('homes-sample.blkparse')
# output: outputs number of uniques for the trace. will return False if not found.
# output example: 523

def mongo_get_unique(trace_name):
    currentTrace = storage.find_trace(trace_name)
    #print(currentTrace)
    if currentTrace != False:
        number_of_uniques = currentTrace.get("unique")
        print("number of uniques gotten", number_of_uniques)
        return number_of_uniques
    else:
        return False
    '''else:
        pretty.utility("trace " +  trace_name + " not found in database... uploading")
        confirmed = sg.sf_singleTraceGen(trace_name)
        trace = storage.find_trace(trace_name)
        number_of_uniques = trace.get("unique")
        if confirmed:
            return number_of_uniques
        else:
            pretty.failure("failed to upload trace to database")
            return False'''


#edited 9/1
'''def mongo_new_rank_csv(config):
    for paths in config['rank']:
        for rank_csv in sg.generateTraceNames(paths):
            storage.insert_csv_run(rank_csv)'''
#edited 9/1
'''def minio_rank_csv_insert(config):
    print("in minio rank csv insert")
    toMinio = Minio_Module.Minio_Module()
    for paths in config['rank']:
        for rank_csv in sg.generateTraceNames(paths):
            df = pd.read_csv(paths)
            cur_csv = storage.find_csv_run(rank_csv)
            csv_id = str(cur_csv.get("_id"))
            if toMinio.exist(csv_id):
                pretty.success(rank_csv + " already in minio store")
            else:
                df.to_csv(csv_id + '_csv_rank' +'.zip', index=False, compression='zip')
                toMinio.insert(csv_id + '_csv_rank' +'.zip', csv_id)
                if toMinio.exist(csv_id):
                    pretty.success(rank_csv + " successfully uploaded")
                else:
                    pretty.success(rank_csv + " upload failed")'''
            #toMinio.insert(hitrate_over_time_output + '.npz', hit_rate_id)
            #toMinio.insert(hitrate_over_time_output + '.npz', hit_rate_id)
            

# as_to_Database: uploads data to mongo and minio
# input: trace, algorithm, cache size, total number of ios, number of hits, total hit rate, total miss rate, pollution 
#        the eviction variables are actually empty at the moment, hit rate over time, miss rate over time, pollution over time,
#        optional arguments for algorithm specific data.
#
# 
# output: returns the corresponding mongo id. this is used to query minio

def as_to_Database(trace, algname, cache_size, ios, hits, hit_rate, misses, pollution, f_eviction_rate, f_eviction_total, hit_ot, miss_ot, pol_ot, minio_only,
    dlirs_HIR_s = None, lecar_lru = None , arc_p = None, cacheus_learning_rate = None, cacheus_lru = None, cacheus_q = None):

        #print("*************************************AS TO DATABASE**********************************")

        currentTrace = trace + "_" + algname + "_" + str(cache_size)
        
        hitrate_over_time_output = "./graph data/"+currentTrace + '-hit_rate'
        missrate_over_time_output = "./graph data/"+currentTrace + '-miss_rate'
        pollutionrate_over_time_output = "./graph data/"+currentTrace + '-pollution'

        toMinio = Minio_Module.Minio_Module()

        np.savez_compressed(hitrate_over_time_output, hit_ot)
        np.savez_compressed(missrate_over_time_output, miss_ot)
        np.savez_compressed(pollutionrate_over_time_output, pol_ot)

        #find a collection that has current trace name, algorithm and cache size and return its ID
        #use this ID for minio uploads

        ###new algorithm outputs###
        #these are contingent on what algorithm is being run as each algorithm has different data that is important to track

        '''lecar_lru_output = currentTrace + "_LECAR_LRU_OVER_TIME"
        arc_p_output = currentTrace + "_ARC_P_OVER_TIME"
        cacheus_learning_rate_output = currentTrace + "_CACHEUS_LEARNING_RATE_OVER_TIME"
        cacheus_lru_output = currentTrace + "_CACHEUS_LRU_OVER_TIME"
        cacheus_q_output = currentTrace = "_CACHEUS_Q_OVER_TIME"

        np.savez_compressed(hitrate_over_time_output, hit_ot)
        np.savez_compressed(missrate_over_time_output, miss_ot)
        np.savez_compressed(pollutionrate_over_time_output, pol_ot)

        ###new algorithm outputs###
        np.savez_compressed(dlirs_stack_output, dlirs_HIR_s)
        np.savez_compressed(lecar_lru_output, lecar_lru)
        np.savez_compressed(arc_p_output, arc_p)
        np.savez_compressed(cacheus_learning_rate_output, cacheus_learning_rate)
        np.savez_compressed(cacheus_lru_output, cacheus_lru)
        np.savez_compressed(cacheus_q_output, cacheus_q)'''


        pretty.utility("~~~~SENDING " + currentTrace + " TO MONGO DB~~~~~~")

        # ------ mongodb storage ------
        
        storage.new_store_alg(ios, hits, hit_rate, misses, pollution, f_eviction_rate, f_eviction_total, algname, cache_size, trace)
        # --------------------- 

        mongo_trace_runs_id = storage.find_trace_run_id(trace, algname, cache_size)


        #hit rate ID for minio
        hit_rate_id = mongo_trace_runs_id + '-hit_rate'
        #miss rate ID for minio
        miss_rate_id = mongo_trace_runs_id + '-miss_rate'
        #pollution rate ID for minio
        pol_rate_id = mongo_trace_runs_id + '-pollution'

        toMinio.insert(hitrate_over_time_output + '.npz', hit_rate_id)
        toMinio.insert(missrate_over_time_output + '.npz', miss_rate_id)
        toMinio.insert(pollutionrate_over_time_output + '.npz', pol_rate_id)

        #######New alg plot data########
        #dlirs HIR stack array ID for minio
        '''dlirs_id = mongo_trace_runs_id + '-dlirs_stack'
        #lecar LRU array for minio
        lecar_lru_id = mongo_trace_runs_id + '-lecar_lru'
        #arc p value array ID for minio
        arc_p_id = mongo_trace_runs_id + '-arc_p'
        #cacheus learning rate array ID for minio
        cacheus_learning_rate_id = mongo_trace_runs_id + '-cacheus_learning_rate'
        #cacheus LRU array ID for minio
        cacheus_lru_id = mongo_trace_runs_id + '-cacheus_lru'
        #cacheus q array ID for minio
        cacheus_q_id = mongo_trace_runs_id + '-cacheus_q'''

        #print("in getAlgStats ", hit_rate_id, '  ', miss_rate_id, ' ', pol_rate_id)
        pretty.utility("trace arrays being inserted to mongo for " + currentTrace)

        #loaded = np.load(outputString +'.npz')

        '''insert both sets of output as seperate npz files'''
        # it is important to note that these compressed files are written to the computer and then sent to Minio
        # currently unsure how to have these compressed objects be variables in memory

        if dlirs_HIR_s != None:
            dlirs_stack_output = "./graph data/"+currentTrace + '-dlirs_stack'
            np.savez_compressed(dlirs_stack_output, dlirs_HIR_s)
            dlirs_id = mongo_trace_runs_id + '-dlirs_stack'
            toMinio.insert(dlirs_stack_output + '.npz', dlirs_id)

        if lecar_lru != None:
            lecar_lru_output = "./graph data/"+currentTrace + '-lecar_lru'
            np.savez_compressed(lecar_lru_output, lecar_lru)
            lecar_lru_id = mongo_trace_runs_id + '-lecar_lru'
            toMinio.insert(lecar_lru_output + '.npz', lecar_lru_id)

        if arc_p != None:
            arc_p_output = "./graph data/"+currentTrace + "_ARC_P_OVER_TIME"
            np.savez_compressed(arc_p_output, arc_p)
            arc_p_id = mongo_trace_runs_id + '-arc_p'
            toMinio.insert(arc_p_output + '.npz', arc_p_id)

        if (cacheus_learning_rate != None) and (cacheus_lru != None) and (cacheus_q != None):
            cacheus_learning_rate_output = "./graph data/"+currentTrace + '-cacheus_learning_rate'
            cacheus_lru_output = "./graph data/"+currentTrace + '-cacheus_lru'
            cacheus_q_output = "./graph data/"+currentTrace + '-cacheus_q'
            np.savez_compressed(cacheus_learning_rate_output, cacheus_learning_rate)
            np.savez_compressed(cacheus_lru_output, cacheus_lru)
            np.savez_compressed(cacheus_q_output, cacheus_q)
            cacheus_learning_rate_id = mongo_trace_runs_id + '-cacheus_learning_rate'
            cacheus_lru_id = mongo_trace_runs_id + '-cacheus_lru'
            cacheus_q_id = mongo_trace_runs_id + '-cacheus_q'
            toMinio.insert(cacheus_learning_rate_output + '.npz', cacheus_learning_rate_id)
            toMinio.insert(cacheus_lru_output + '.npz', cacheus_lru_id)
            toMinio.insert(cacheus_q_output + '.npz', cacheus_q_id)

        #####NEW ALGORITHM ARRAYS
        '''toMinio.insert(dlirs_stack_output + '.npz', dlirs_id)
        toMinio.insert(lecar_lru_output + '.npz', lecar_lru_id)
        toMinio.insert(arc_p_output + '.npz', arc_p_id)
        toMinio.insert(cacheus_learning_rate_output + '.npz', cacheus_learning_rate_id)
        toMinio.insert(cacheus_lru_output + '.npz', cacheus_lru_id)
        toMinio.insert(cacheus_q_output + '.npz', cacheus_q_id)'''

        return mongo_trace_runs_id

# as_minio_confirm: confirms that data for a given trace/alg/cache size was uploaded successfully
# input: trace id, trace name, algorithm, cache size
# input example: as_minio_confirm('5eb2a7f95ef07cbca3668020', 'homes-sample.blkparse', 'arc', 0.2)
# output: queries minio for the existence of files with traceId + '-plot'. 
#         this traceId corresponds to tracename-algorithm-cachesize combination
# output example: returns true if everything was successfully uploaded, returns false if there was a failure.

def as_minio_confirm(traceId, traceName, algname, cache_size):
    fullTraceName = traceName + " " + algname + " " + str(cache_size)
    toMinio = Minio_Module.Minio_Module()

    pretty.utility("CONFIRMING IF ARRAYS FOR " +  fullTraceName  +" WERE UPLOADED SUCCESSFULLY")

    hit_rate_id = traceId + '-hit_rate'
    miss_rate_id = traceId + '-miss_rate'
    pollution_id = traceId + '-pollution'

    if algname.lower() == 'dlirs':
        dlirs_stack_id = traceId + '-dlirs_stack'
        if toMinio.exist(dlirs_stack_id):
            storage.trace_run_confirmed(traceId, dlirs = 1)
        else:
            return False

    if algname.lower() == 'lecar':
        lecar_lru_id = traceId + '-lecar_lru'
        if toMinio.exist(lecar_lru_id):
            storage.trace_run_confirmed(traceId, lecar = 1)
        else:
            return False

    if algname.lower() == 'arc':
        arc_p_id = traceId + '-arc_p'
        if toMinio.exist(arc_p_id):
            storage.trace_run_confirmed(traceId, arc = 1)
        else:
            return False

    if algname.lower() == 'cacheus':
        cacheus_learning_rate_id = traceId + '-cacheus_learning_rate'
        cacheus_lru_id = traceId + '-cacheus_lru'
        cacheus_q_id = traceId + '-cacheus_q'
        if toMinio.exist(cacheus_learning_rate_id) and toMinio.exist(cacheus_lru_id) and toMinio.exist(cacheus_q_id):
            storage.trace_run_confirmed(traceId, cacheus = 1)
        else:
            return False

    if toMinio.exist(hit_rate_id):
        storage.trace_run_confirmed(traceId, hit_rate = 1)
    else:
        pretty.failure("Hit rate array for " + fullTraceName + "to minio failed")
        return False

    if toMinio.exist(hit_rate_id):
        storage.trace_run_confirmed(traceId, miss_rate = 1)
    else:
        pretty.failure("Miss rate array for " + fullTraceName + "to minio failed")
        return False

    if toMinio.exist(hit_rate_id):
        storage.trace_run_confirmed(traceId, pollution = 1)
    else:
        pretty.failure("Pollution rate array for " + fullTraceName + "to minio failed")
        return False

    pretty.success("==============================" + fullTraceName + " succesfully uploaded ==========================================")
    return True

#this method uploads the data generated by the -s flag to mongo and minio databases
def s_to_database(trace, num_req, num_unique, num_reuse, num_writes, num_requests, req, histogram, reuse_distance, time_stamp, minio_only):

        pretty.utility("~~~~SENDING " + trace + " TO MONGO DB~~~~~~")
        #print("IN S TO DATABASE METHOD")
        #requestFrequencyOutput = trace + "_REQUEST_FREQ"  
        requestsOutput = "./graph data/"+trace + '_rq'
        histogramOutput = "./graph data/"+trace + '_histogram'
        reuseOutput = "./graph data/"+trace + '_reuse'
        timeStampOutput = "./graph data/"+trace + '_time'

        #np.savez_compressed(requestFrequencyOutput, histogram)
        np.savez_compressed(requestsOutput, req)
        np.savez_compressed(histogramOutput, histogram)
        np.savez_compressed(reuseOutput, reuse_distance)
        np.savez_compressed(timeStampOutput, time_stamp)

        # np.savez_compressed(trace, req, regFreq, misses, hitPerc, ios, polOT, missRate)

        # ------ db storage -------
        if not minio_only:
            storage.store_workload(trace, num_req, num_unique, num_reuse,
                num_writes, num_requests)

        mongo_trace_id = str(storage.find_id(trace))
        if mongo_trace_id:
            #Request frenquency ID for minio
            #rqfId = mongo_trace_id + '-rqf' 
            #Request ID for minio
            rqId = mongo_trace_id + '-rq' 

            #histogram ID for minio
            hId = mongo_trace_id + '-histogram'

            #reuse distance ID for minio
            reuId = mongo_trace_id + '-reuse'

            #time stamp ID for minio
            timeId = mongo_trace_id + '-time'

            #print("in single trace gen ", rqfId, '  ', rqId)
            pretty.utility("trace being inserted to minio " + trace)

            #loaded = np.load(outputString +'.npz')

            '''insert both sets of output as seperate npz files'''
            # it is important to note that these compressed files are written to the computer and then sent to Minio
            # currently unsure how to have these compressed objects be variables in memory
            toMinio = Minio_Module.Minio_Module()
            #toMinio.insert(requestFrequencyOutput +'.npz', rqfId)
            toMinio.insert(requestsOutput + '.npz', rqId)
            toMinio.insert(histogramOutput + '.npz', hId)
            toMinio.insert(reuseOutput + '.npz', reuId)
            toMinio.insert(timeStampOutput + '.npz', timeId)

        return mongo_trace_id

#def upload_rank_csv(file):



#confirm that data was succesfully sent to minio
#update mongodb if true
def s_minio_confirm(traceId, traceName):
    toMinio = Minio_Module.Minio_Module()

    hId = traceId + '-histogram'
    #rqfId = traceId + 'rqf'
    rqId = traceId + '-rq'

    reuId = traceId + '-reuse'

    timeId = traceId + '-time'

    if toMinio.exist(hId):
        storage.workload_confirmed(traceName, requestFrequency = 1)
    else: 
        pretty.failure("Request frequency upload for " + traceName + " to minio failed")
        return False

    if toMinio.exist(rqId):
        storage.workload_confirmed(traceName, request = 1)
    else: 
        pretty.failure("Request frequency upload for " + traceName + " to minio failed")
        return False

    if toMinio.exist(reuId):
        storage.workload_confirmed(traceName, reuseDistance = 1)
    else: 
        pretty.failure("Reuse distance upload for " + traceName + " to minio failed")
        return False

    if toMinio.exist(timeId):
        storage.workload_confirmed(traceName, time = 1)
    else: 
        pretty.failure("Real time array upload for " + traceName + " to minio failed")
        return False
    pretty.success("s_minio_confirm"  + traceName + "confirmed uploaded to database")
    return True

def catch_config_errors(config):
    valid_algs = ['alecar6', 'arc', 'arcalecar', 'cacheus', 
                    'dlirs', 'lecar', 'lfu', 'lirs', 'lirsalecar', 'lru', 'mru']
    invalid_algs = []
    for algs in set(config['algorithms']):
        if algs.lower() not in valid_algs:
            pretty.failure("invalid algorithm:"+ algs + " detected")
            invalid_algs.append(algs)
            #invalid_algs = True
    invalid_cache_size = []
    for sizes in config['cache_sizes']:
        st = str(sizes)
        if sizes > 1.0:
            invalid_cache_size.append(sizes)
        if sizes <= 0:
            invalid_cache_size.append(sizes)

    return invalid_algs, invalid_cache_size



def catch_json_errors(conf):
    try:
        conf = json.loads(conf)
        return conf
    except json.JSONDecodeError as e:
        pretty.failure("There was an error decoding the uploaded file to JSON it is possible you are missing a comma or have written a decimal value without a leading zero")
        pretty.failure(e)
        return False
