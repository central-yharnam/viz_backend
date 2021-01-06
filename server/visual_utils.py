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
import server_utils as serv
import pandas as pd
#import perm
import Minio_Module
import math
import pretty
#import api
import conduit
import time

#this data is hardcoded for convenience but it also exists in mongo as tracked_plots
#plot input data for each flag, the format is:
#-flag: type_of_data [0], type_of_graph [1], minio_id_suffix [2], x_axis label [3], y_axis label[4], title[5], is it algorithm specific?[6]
ot_graph_xlabels = ['Request Index', 'Time']
ot_graph_titles = ['at Request Index', 'Over Time']

FLAG=0
TRACE=1
ALGR=2
SIZE=3

plots = {'-p': ['trace', 'scatter', '-rq', ot_graph_xlabels, 'Logical Block Address Accessed', 'Access Pattern',  False ],
         '-r': ['trace', 'histogram', '-reuse', 'Reuse Distance', 'Frequency of Reuse Distance', 'Reuse Distance Frequency Distribution', False],
         '-g': ['trace', 'histogram', '-histogram', 'Times LBA Reaccessed', 'Frequency of Reaccess', 'Frequency Distribution of Accesses', False], 
         '-H': ['algorithm','line', '-hit_rate', ot_graph_xlabels, 'Hit Rate', ot_graph_titles, False],
         '-P': ['algorithm','line', '-pollution', ot_graph_xlabels, 'Pollution', ot_graph_titles, False],
         '-m': ['algorithm','line', '-miss_rate', ot_graph_xlabels, 'Miss Rate', ot_graph_titles, False],  
         '-l': ['algorithm','line', '-lecar_lru', ot_graph_xlabels, 'Weight of LRU', ot_graph_titles, True],
         '-w': ['algorithm','line', '-arc_p', ot_graph_xlabels, 'Value of Arc P', ot_graph_titles, True],
         '-d': ['algorithm','line', '-dlirs_stack', ot_graph_xlabels, 'Dlirs Stack Size', ot_graph_titles, True],
         '-y': ['algorithm','line', '-cacheus_lru', ot_graph_xlabels, 'Weight of LRU', ot_graph_titles, True],
         '-x': ['algorithm','line', '-cacheus_learning_rate', ot_graph_xlabels, 'Cacheus Learning Rate', ot_graph_titles, True],
         '-z': ['algorithm','line', '-cacheus_q', ot_graph_xlabels, 'Cacheus SR Stack Size', ot_graph_titles, True]
}

#methods for updating the list of tracked plots
#really they should be in server utils with the rest of the server contacting stuff but it made more sense to look at these methods next to the plots they're tracking
def flag_util():
    for key in plots:
        storage.store_flag(key, plots[key])
def flag_del():
    for key in plots:
        storage.delete_plots_tracked(key)



# process_histogram: extra data is put into the histogram arrays because additional processing is needed for each.
# input: corresponding flag, frequency array
# example input: process_histogram('-g', frequency_map)
# output: x and y values for frequency distribution

def process_histogram(flag, array):

    hist_data = array['arr_0']
    hist_data = hist_data[()]

    print("IN PROCESS HISTOGRAM")

    # -g is for plotting access frequency. the range for the x axis starts at 2 because the number of unique accesses, which corresponds to 
    # an x value of 1 will throw off the graphing so it is ignored and placed in the title of the plot.
    if flag == '-g':
        max_frequency = hist_data[0]
        uniques = hist_data[1]
        to_plot = []
        del hist_data[0] #index 0 holds the maxmimum number of reuses
        for i in range(2, max_frequency + 1):
            to_plot.append(hist_data[i])

        x_axis = list(range(2, max_frequency + 1))

        return x_axis, to_plot, uniques
    # -r is for plotting reuse distance frequencies. ie: how many LBAs have a reuse distance of 5 and so on.
    if flag == '-r':
        #to_plot = reuse_distribution(hist_data)
        to_plot = reuse_distrib(hist_data)
        x_axis = list(range(0,len(to_plot)))
        return x_axis, to_plot


# reuse array is a dictionary of lists where the key is the LBA. the value is a list of when that LBA was called. we go through each of these
# lists to determine the frequency of reuse distances
def reuse_distrib(reuse_array):
    
    reuse_distance_frequency = {}
    reuse_result = np.array([])
    reuse_result = np.append(reuse_result, 0)

    del reuse_array['max_reused']
    max_reuse_distance = 0
    #print(reuse_array)
    count = 0
    for lba in reuse_array:
        count += 1
        #print(count)
        lba_reuse_history = reuse_array[lba]
        if len(lba_reuse_history) != 1:
            #print(lba_reuse_history)
            for i in range(0, len(lba_reuse_history) - 1):
                #print(i, len(lba_reuse_history) - 1, "reuse history")
                current_reuse_distance = lba_reuse_history[i+1] - lba_reuse_history[i]
                if current_reuse_distance > max_reuse_distance:
                    max_reuse_distance = current_reuse_distance
                if reuse_distance_frequency.get(current_reuse_distance) == None:
                    reuse_distance_frequency[current_reuse_distance] = 1
                else:
                    reuse_distance_frequency[current_reuse_distance] += 1
                #reuse_distance_frequency[current_reuse_distance-1] += 1
    
    print(max_reuse_distance)
    for i in range(1, max_reuse_distance+1):
        if reuse_distance_frequency.get(i) == None:
            reuse_result = np.append(reuse_result, 0)
        else:
            reuse_result = np.append(reuse_result, reuse_distance_frequency[i])
    #print(reuse_result)
    return reuse_result



# visualize_data: this is the main loop that gets data, processes it and then plots it.
#				  there are 3 cases though 1 can be thought of as a subcase of the other.
#
#				  Case 1: We want to plot trace data, this would be plotting the access pattern for the workload 
#						  or one of the frequency distribution graphs. 
#
#				  Case 2: We want to plot alg data. In this case we must go through every algorithm and cache size specified in the config.
#						  These are plots like pollution and hit rate.
#
#				  Case 3 (or 2a): We want to plot alg data, but only alg specific data such as the learning rate for cacheus.
#								  in this case we do not go through the list of algs in the config because it is irrelevant. 
#								  Iterate through all cache sizes and get relevant data to plot.
#
# input: flag, config, boolean that represents if real time of virtual time is wanted
#
# example input: visualize_data('-H', config, 1)
#				 for virtual time, pass 0. virtual time is simply the number of requests. 
#				 at this point virtual time is deprecated so in all cases 1 should be passed. 
# output: desired plots


def visualize_data(flag, config, y_scale=None):


    minio_get = Minio_Module.Minio_Module()
    graph = sv.StatVis()
    current_plot = plots[flag]
    #plots that use trace data have a different, smaller loop than the plots using data from algorithms
    if current_plot[0] == 'trace':
        for traces in config['traces']:
            for trace_name in sg.generateTraceNames(traces):
                print(trace_name + "=======================================")
                #request data from mongo
                out_file = serv.mongo_get_trace_run_plot_data(trace_name, current_plot[2], minio_get)
                if out_file:
                    #load that data
                    out_file = np.load(out_file, allow_pickle = True) #uncompress

                   
                    if current_plot[1] == 'histogram':
                        #---
                        if flag == '-g':
                            x_axis, frequency, uniques = process_histogram(flag, out_file)
                            graph.vis_data(current_plot[1], current_plot[3], current_plot[4], 
                                str(trace_name) + " " + current_plot[5] + " Number of Uniques: " + str(uniques), frequency, config['output_path'], x_data = x_axis)
                        else:
                            x_axis, frequency = process_histogram(flag, out_file)
                            #print(frequency)
                            '''graph.vis_data(current_plot[1], current_plot[3], current_plot[4], 
                                str(trace_name) + " " + current_plot[5], frequency, x_data = x_axis)'''
                            #this is hard coded as line because it will not render as a bar graph, it lags and never finishes
                            graph.vis_data('line', current_plot[3], current_plot[4], 
                                str(trace_name) + " " + current_plot[5], frequency, config['output_path'],x_data = x_axis)
                        #---
                    else:
                        #---
                        over_time = serv.get_over_time_list(trace_name, minio_get)  
                        graph.vis_data(current_plot[1], current_plot[3][1], current_plot[4], 
                             str(trace_name) + " " + current_plot[5], out_file['arr_0'], config['output_path'], x_data = over_time)
                        #---
                        
                            
                else:
                    pretty.failure("error downloading" + trace_name + 'access pattern')
    #if it is an algorithm data plot and that data is not algorithm specific, run a loop for all algorithms
    elif current_plot[0] == 'algorithm' and current_plot[6] == False:
        for traces in config['traces']:
            for trace_name in sg.generateTraceNames(traces):
                for algorithms in config['algorithms']:
                    for cache_size in config['cache_sizes']:
                        percent_cache = cache_size
                        uniques = serv.mongo_get_unique(trace_name)
                        if uniques:
                            cache_size = math.floor(cache_size * serv.mongo_get_unique(trace_name))
                        else:
                            return False

                        if cache_size >= 10:
                            out_file = serv.mongo_get_alg_run_plot_data(config, current_plot[2], trace_name, algorithms, cache_size, minio_get)
                            plot_title = current_plot[5][1]
                            #print(plot_title)
                            if out_file:
                                full_title = str(trace_name) + " " + str(algorithms) + "_" + str(cache_size) + " " + current_plot[4] + " " + plot_title
                                out_file = np.load(out_file, allow_pickle = True)
                                over_time = serv.get_over_time_list(trace_name, minio_get)
                                #print(trace_name, algorithms, cache_size)
                                #print("=====================")
                                graph.vis_data(current_plot[1], current_plot[3][1], current_plot[4], 
                                    full_title, out_file['arr_0'], config['output_path'], x_data = over_time)
                                #print("++++++++++++++++++++")
                            else:
                                pretty.failure("error downloading " + trace_name + current_plot[2])

                        else:
                            pretty.utility(trace_name + " not big enough for current cache size percentage " + str(percent_cache) )
    #else, it is an algorithm specific plot. the only difference here is that there is not looping through the list of algorithms
    elif current_plot[0] == 'algorithm':
        for traces in config['traces']: 
            for trace_name in sg.generateTraceNames(traces):
                for cache_size in config['cache_sizes']:

                    percent_cache = cache_size

                    uniques = serv.mongo_get_unique(trace_name)
                    if uniques:
                        cache_size = math.floor(cache_size * serv.mongo_get_unique(trace_name))
                    else:
                        return False

                    if cache_size >= 10:
                        
                        #all of the algorithm specific plots have the name of the algorithm before the '_'
                        #so that is why algorithm_used[0] is called, we must also remove the '-' that is in the zero index

                        algorithm_used = current_plot[2].split('_') 
                        algorithm_used = algorithm_used[0]
                        algorithm_used = algorithm_used[1:len(algorithm_used)]
                        
                        #pretty.utility(algorithm_used)
                        out_file = serv.mongo_get_alg_run_plot_data(config, current_plot[2], trace_name, algorithm_used, cache_size, minio_get)
                        plot_title = current_plot[5][1]
                        #pretty.utility(plot_title)
                        if out_file:
                            full_title = str(trace_name) + " " + str(algorithm_used) + "_" + str(cache_size) + " " + current_plot[4] + " " + plot_title
                            out_file = np.load(out_file, allow_pickle = True)

                            over_time = serv.get_over_time_list(trace_name, minio_get)
                            pretty.utility(trace_name + algorithm_used + str(cache_size) )
                            graph.vis_data(current_plot[1], current_plot[3][1], current_plot[4], 
                                full_title, out_file['arr_0'], config['output_path'], x_data = over_time)
                            #---
                            #
                        else:
                            pretty.failure("error downloading " + trace_name + current_plot[2])

                    else:
                        pretty.utility(trace_name + " not big enough for current cache size percentage " + str(percent_cache) )
 


# checks if the cache size is large enough and 
# then outputs a list where entries are organized like this
# {"plot":flag, "trace_name":trace, "algorithm":None, "cache_size":None, "kwargs": None}
# utility for organizing data for webapp
def config_permutation_gen(config, flags):
    params = []
    '''print(config['traces'], "hello")
    print(flags)
    for flag in flags:
        current_plot = plots[flag]
        if current_plot[0] == 'algorithm':
            for trace in config['traces']:
                pairs = gen_all_pairs(config['algorithms'])'''

    for flag in flags:
        current_plot = plots[flag]
        if current_plot[0] == 'trace':
            for trace in config['traces']:
                params.append({"plot":flag, "trace_name":trace, "algorithm":None, "cache_size":None, "kwargs": None})
        elif current_plot[0] == 'algorithm':
            #   either for all algorithms or a specific one
            #   determined by plot type
            algorithms = config['algorithms'] 
            if current_plot[6] == True:
                a = current_plot[2].split('_')[0]
                if a[1:] in algorithms: algorithms = [a[1:]]
                else: 
                    params.append({"Error": current_plot[2] + " plot for " + a })
                    continue
            for trace in config['traces']:
                for algorithm in algorithms:
                    print(algorithm, "========================================")
                    for cache_size in config['cache_sizes']:
                        print(cache_size, "cache size")
                        percent_cache = cache_size
                        uniques = serv.mongo_get_unique(trace)
                        if uniques:
                            cache_size = math.floor(cache_size * uniques)
                        else: 
                            params.append({"Error": " uniques for " + trace })
                    if cache_size >= 10:
                        params.append({"plot":flag, "trace_name":trace, "algorithm":algorithm, "cache_size":cache_size, "kwargs": None})
                    else:
                        pass
                        #return "Cache size for trace too small"
    return params


# this method generates graph data for a single set of parameters
# main flow encapsulated here.
# 
def s_generate_graph_data(config, params, app_id):
    print("s generate graph data")
    minio_get = Minio_Module.Minio_Module()
    current_plot = plots[params['plot']] 
    print(params, "s generate graph data")
    if current_plot[0] == 'trace':
        out_file = serv.mongo_get_trace_run_plot_data(params['trace_name'], current_plot[2], minio_get, app_id)
        if out_file:
            #out_file = np.load(out_file, allow_pickle = True)
            if current_plot[1] == 'histogram':
                if params['plot'] == '-g':
                    conduit.current_status[app_id] = "Processing histogram, please wait... This process may take over 10 minutes."
                    x_axis, frequency, uniques = process_histogram(params['plot'], out_file)
                    return x_axis, frequency, (str(params['trace_name']) + ' Number of Unique Accesses: ' + str(uniques) )
                else:
                    conduit.current_status[app_id] = "Processing histogram, please wait... This process may take over 10 minutes."
                    x_axis, frequency = process_histogram(params['plot'], out_file)
                    conduit.current_status[app_id] = "Rendering " + params['trace_name'] +  " graph..."
                    return x_axis, frequency, str(params['trace_name']) 
            else:
                over_time = serv.get_over_time_list(params['trace_name'], minio_get, app_id)  
                conduit.current_status[app_id] = "Rendering " + params['trace_name'] +  " graph..."
                return over_time, out_file['arr_0'][()], str(params['trace_name'])
        else:
            pretty.failure("problem with retrieving files from database") 
    elif current_plot[0] == 'algorithm':
        out_file = serv.mongo_get_alg_run_plot_data(config, current_plot[2], params['trace_name'],
                    params['algorithm'], int(params['cache_size']), minio_get, app_id)
       
        plot_title = current_plot[5][1]
        if out_file:
            full_title = str(params['trace_name']) + " " + str(params['algorithm']) + "_" + str(params['cache_size']) + " " + current_plot[4] + " " + plot_title
            #out_file = np.load(out_file, allow_pickle = True)
            conduit.current_status[app_id] = "Generating over time data for" + params['trace_name'] +  "please wait..."
            over_time = serv.get_over_time_list(params['trace_name'], minio_get, app_id)
            conduit.current_status[app_id] = "Rendering " + params['trace_name'] +  " graph..."
            return over_time, out_file['arr_0'][()], full_title
        else:
            conduit.current_status[app_id] = "error getting graph data"
            return None, None, None


#calls the server utils to retrieve the Y value array from the database or disk and delivers to api
def generate_y(config, params, app_id):
    current_plot = plots[params['plot']]
    plot_title = current_plot[5][1]
    full_title = str(params['trace_name']) + " " + str(params['algorithm']) + "_" + str(params['cache_size']) + " " + current_plot[4] + " " + plot_title
    minio_get = Minio_Module.Minio_Module()

    print("IN GENERATE Y")
    print(params['cache_size'])

    uniques = serv.mongo_get_unique(params['trace_name'])
    if uniques:
        cache_size = math.floor(params['cache_size'] * uniques)

    out_file = serv.mongo_get_alg_run_plot_data(config, current_plot[2], params['trace_name'],
                    params['algorithm'], cache_size, minio_get, app_id)
    # out_file = np.load(out_file, allow_pickle = True) # **************************************
    return out_file['arr_0'][()], full_title

        

# visualize_data_mult: quite similar to visualize_data except that multiple graphs are superimposed on each other.
#					   it superimposes the first 4 cache sizes and then ignores the rest. 
#						
#				  Case 1: We want to plot trace data, this would be plotting the access pattern for the workload 
#						  or one of the frequency distribution graphs. 
#
#				  Case 2: We want to plot alg data. In this case we must go through every algorithm and cache size specified in the config.
#						  These are plots like pollution and hit rate.
#
#				  Case 3 (or 2a): We want to plot alg data, but only alg specific data such as the learinng rate for cacheus.
#								  in this case we do not go through the list of algs in the config because it is irrelevant. 
#								  Iterate through all cache sizes and get relevant data to plot.
#
# input: flag, config, boolean that represents if real time of virtual time is wanted
#
# example input: visualize_data('-H', config, 1)
#				 for virtual time, pass 0. virtual time is simply the number of requests. 
#				 at this point virtual time is deprecated so in all cases 1 should be passed. 
# output: desired plots


def visualize_data_multi(flag, config, y_scale = None):


    minio_get = Minio_Module.Minio_Module()
    graph = sv.StatVis()

    multi_plot = []
    multi_labels = [] #max 4 plots for multi graphing

    current_plot = plots[flag]
    #plots that use trace data have a different, smaller loop than the plots using data from algorithms
    if current_plot[0] == 'trace':
        for traces in config['traces']:
            for trace_name in sg.generateTraceNames(traces):
                print(trace_name + "=======================================")
                out_file = serv.mongo_get_trace_run_plot_data(trace_name, current_plot[2], minio_get)
                if out_file:
                    #plot_minio_data_request('lba accessed ', trace_name + " \nAccess Pattern", out_file, graph, scatter = 1)
                    out_file = np.load(out_file, allow_pickle = True)

                    if current_plot[1] == 'histogram':
                        #print(out_file)
                        x_axis, frequency = process_histogram(flag, out_file)
                        graph.vis_data(current_plot[1], current_plot[3], current_plot[4], 
                        str(trace_name) + " " + current_plot[5], frequency, config['output_path'], x_data = x_axis, scale=y_scale)
                    else:
                        #over_time = get_over_time_list(trace_name, minio_get)  

                        multi_plot.append(out_file['arr_0'])
                        multi_labels.append(trace_name)
                        #graph.vis_data(current_plot[1], current_plot[3][req_time], current_plot[4], 
                        #    str(trace_name) + " " + current_plot[5], out_file['arr_0'], x_data = over_time)

                else:
                    print("error downloading", trace_name, 'access pattern')


            print("==================================$$$$============================================")
            over_time = serv.get_over_time_list(trace_name, minio_get)
            graph.vis_data_multi(current_plot[1], current_plot[3][req_time], current_plot[4], 
                        str(trace_name) + " " + title, multi_plot, multi_labels, config['output_path'], x_data = over_time, scale=y_scale)
            multi_plot = []
            multi_labels = []

    elif current_plot[0] == 'algorithm' and current_plot[6] == False:
        for traces in config['traces']:
            for trace_name in sg.generateTraceNames(traces):
                for algorithms in config['algorithms']:
                    for cache_size in config['cache_sizes']:
                        percent_cache = cache_size
                        cache_size = math.floor(cache_size * serv.mongo_get_unique(trace_name))

                        if cache_size >= 10:
                            #mongo_get_alg_run_plot_data(config, '-pollution')
                            out_file = serv.mongo_get_alg_run_plot_data(config, current_plot[2], trace_name, algorithms, cache_size, minio_get)
                            plot_title = current_plot[5][1]
                            plot_title = str(trace_name) + " " + str(algorithms) + " " + current_plot[4]  + plot_title
                            print(plot_title)
                            if out_file:
                                out_file = np.load(out_file, allow_pickle = True)
                                multi_plot.append(out_file['arr_0'])
                                multi_labels.append(cache_size)
                            else:
                                print("error downloading", trace_name, 'access pattern')

                        else:
                            print(trace_name, " not big enough for current cache size percentage ", percent_cache)
                    if cache_size >= 10:
                        print("==================================DOING OVER TIME============================================")
                        over_time = serv.get_over_time_list(trace_name, minio_get)
                        graph.vis_data_multi(current_plot[1], current_plot[3][1], current_plot[4], 
                            str(trace_name) + " " + plot_title, multi_plot, multi_labels, config['output_path'], x_data = over_time, scale=y_scale)
                        multi_plot = []
                        multi_labels = []

    elif current_plot[0] == 'algorithm':
        for traces in config['traces']: 
            for trace_name in sg.generateTraceNames(traces):
                for cache_size in config['cache_sizes']:
                    percent_cache = cache_size
                    cache_size = math.floor(cache_size * serv.mongo_get_unique(trace_name))
                    if cache_size >= 10:
                        
                        #all of the algorithm specific plots have the name of the algorithm before the '_'
                        #so that is why algorithm_used[0] is called, we must also remove the '-' that is in the zero index

                        algorithm_used = current_plot[2].split('_') 
                        algorithm_used = algorithm_used[0]
                        algorithm_used = algorithm_used[1:len(algorithm_used)]
                        
                        print(algorithm_used)
                        out_file = serv.mongo_get_alg_run_plot_data(config, current_plot[2], trace_name, algorithm_used, cache_size, minio_get)
                        plot_title = current_plot[5][1]
                        plot_title = str(trace_name) + " " + str(algorithm_used) + " " + current_plot[4] + " " + plot_title
                        print(plot_title)
                        if out_file:
                            
                            out_file = np.load(out_file, allow_pickle = True)
                            multi_plot.append(out_file['arr_0'])
                            multi_labels.append(cache_size)
                        else:
                            print("error downloading", trace_name, 'access pattern')

                    else:
                        print(trace_name, " not big enough for current cache size percentage ", percent_cache)
                
                if cache_size >= 10:
                    print("==================================$$$$============================================")
                    over_time = serv.get_over_time_list(trace_name, minio_get)
                    graph.vis_data_multi(current_plot[1], current_plot[3][req_time], current_plot[4], 
                        str(trace_name) + " " + plot_title, multi_plot, multi_labels, config['output_path'], x_data = over_time, scale=y_scale)
                    multi_plot = []
                    multi_labels = []


#generates all pairs of algorithms for the overlay plots in visualapiEX
def gen_all_pairs(array):
    final = []
    for indexes in range(len(array)):
        arr = []
        for combi in range(indexes+1, len(array)):
            arr.append([array[indexes],array[combi]])
        if len(arr) != 0:
            final += arr
    return final

# visualize_head_to_head: very similar to visualize data multigenerates overlay graphs with fill
#                       
#                 Case 1: We want to plot trace data, this would be plotting the access pattern for the workload 
#                         or one of the frequency distribution graphs. 
#
#                 Case 2: We want to plot alg data. In this case we must go through every algorithm and cache size specified in the config.
#                         These are plots like pollution and hit rate.
#
#                 Case 3 (or 2a): We want to plot alg data, but only alg specific data such as the learinng rate for cacheus.
#                                 in this case we do not go through the list of algs in the config because it is irrelevant. 
#                                 Iterate through all cache sizes and get relevant data to plot.
#
# input: flag, config, boolean that represents if real time of virtual time is wanted
#
# example input: visualize_data('-H', config, 1)
#                for virtual time, pass 0. virtual time is simply the number of requests. 
#                at this point virtual time is deprecated so in all cases 1 should be passed. 
# output: desired plots

def visualize_head_to_head(config, flag, y_scale = None):
    pretty.utility("generating comparison data for all pairs of algorithms and cache sizes")
    minio_get = Minio_Module.Minio_Module()
    graph = sv.StatVis()

    current_plot = plots[flag]

    #if current_plot[0] == 'algorithm' and current_plot[6] == False:

    all_pairs = gen_all_pairs(config['algorithms'])


    all_plots = {}

    # generate all output arrays here and add them to a dictionary to be referenced for the graphing of all pairs to prevent repeatedly downloading and extracting
    # the same data
    for traces in config['traces']:
        for trace_name in sg.generateTraceNames(traces):
            for algorithms in config['algorithms']:
                for cache_size in config['cache_sizes']:
                    percent_cache = cache_size
                    uniques = serv.mongo_get_unique(trace_name)
                    if uniques:
                        cache_size = math.floor(cache_size * serv.mongo_get_unique(trace_name))
                    else:
                        return False

                    if cache_size >= 10:
                        out_file = serv.mongo_get_alg_run_plot_data(config, current_plot[2], trace_name, algorithms, cache_size, minio_get)
                        if out_file:
                            out_file = np.load(out_file, allow_pickle = True)
                            out_file = out_file['arr_0']
                        all_plots[str(trace_name)+str(algorithms)+str(cache_size)] = out_file
                    else:
                        pretty.failure("error downloading " + trace_name + current_plot[2])

                else:
                    pretty.utility(trace_name + " not big enough for current cache size percentage " + str(percent_cache) )

    compare = []
    for traces in config['traces']:
        for trace_name in sg.generateTraceNames(traces):
            over_time = serv.get_over_time_list(trace_name, minio_get)
            for cache_size in config['cache_sizes']:
                percent_cache = cache_size
                uniques = serv.mongo_get_unique(trace_name)
                if uniques:
                    cache_size = math.floor(cache_size * serv.mongo_get_unique(trace_name))
                else:
                    return False

                if cache_size >= 10:
                    for pairs in all_pairs:
                        compare.append(all_plots[str(trace_name)+str(pairs[0])+str(cache_size)])
                        compare.append(all_plots[str(trace_name)+str(pairs[1])+str(cache_size)])
                        over_time = serv.get_over_time_list(trace_name, minio_get)
                        basename = os.path.basename(trace_name)
                        name = basename + " " + " cache size " + str(cache_size) + " " + str(pairs[0]) + " compared with " + str(pairs[1])
                        print(name)
                        graph.vis_data_multi(current_plot[1], current_plot[3][1], current_plot[4], name, 
                            compare, pairs, config['output_path'], x_data = over_time, scale=y_scale, fill = True)
         
                        compare = []



