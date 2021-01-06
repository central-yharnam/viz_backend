import flask
from flask import request, jsonify

import base64
import json
import requests


import visual_utils as vsu
import server_utils as svr
import storage2
import Minio_Module
#import visual.StatVis as sv

import csv_plot as csvp

import numpy as np
import time
import random

import sys
import conduit


app = flask.Flask(__name__)
#app.config["DEBUG"] = True


app_id = str(time.time()) + str(random.random())


@app.route('/')
def home():
    return "backend is running..."


# returns all the configs that are stored in mongo
# these are the options in "Pick Existing"
@app.route('/mongo_conf', methods=['GET'])
def mongo_configs():
    print("================================")
    print("Greetings from mongo_configs")
    print("================================")
    conf_list = []
    '''for c in storage2.find_in_collection('configs'):
        print(c)
        c['_id'] = str(c['_id'])
        name = c.pop('name', None)
        conf_list.append(        {name: c}        )'''

    conf_list = storage2.find_in_collection('configs')

    print(conf_list, "mongo_configs output")
    return jsonify(str(conf_list))

# takes a form with the user specified config as well as a list of parameters indicating what type of graph is to be plotted
# get_graph is called once for each algorithm, cache size and plot permutation. 
# if someone makes a request for ikki-1 hit rate and miss rate graph at .05 cache size, get_graph is called twice, once for hit rate and once for miss rate.
# if someone makes a request for ikki-1 and ikki-2 hit rate at .05 cache size, get_graph is called twice, once for each trace. 

@app.route('/get_graph', methods=['POST']) #allow POST requests
def get_graph():

    print("================================")
    print("Greetings from get_graph")
    print("================================")

    #conf = request.form.get('config')
    '''conf = request.form['config']
    params = request.form['params']
    app_id = request.form['id']
    conf_response = jsonify(conf)'''

    args = request.json
    conf = args['config']
    #params = args['params']
    plot = args['plot']
    trace_name = args['trace_name']
    algorithm = args['algorithm']
    cache_size = args['cache_size']
    #params = [plot, trace_name, algorithm]

    app_id = args['id']

    print(conf, " webapp input")
    print(args, " webapp input")
    print(app_id, " webapp input")
    # this is necessary because when sending the config over to the API, the " " in the config turn to ' ',
    # these have no sematic value in JSON, conf cannot be turned to JSON without this replacement 
    # the generate_graph_data function expects JSON for the config.
    #conf = conf.replace('\'', '\"')

    #params input comes in as a string. these function calls turn it back into a list for processing within the visual utils function
    #params = params.replace('\'','')[1:-1].split(', ') 
    x, y, title = vsu.s_generate_graph_data(json.loads(conf), args, app_id)

    #print('graph gotten ++++++++++++++++++++++++++++++++++++++++++++++')
    #the response must be only 1 item. 
    y = list(y)
    print( type(x), " x axis: get_graph api output")
    print(type(y), " y axis: get_graph api output")
    print( title, " title: get_graph api output")

    #print(x[0:10], y[0:10], title, "GET GRAPH RESULTS")
    #return str(0)
    return jsonify(xaxis=str(x), yaxis=str(y), res_title=str(title) )


#get_y_axis returns the y values and title for the plot on the front end, which is the data that will change for each cache size and algorithm
#this is to prevent repeated transferring of the same time data through get_graph for multiple cache sizes or algorithms of the same trace.

@app.route('/get_y_axis', methods=['POST'])
def get_y_axis():

    print("================================")
    print("Greetings from get_y")
    print("================================")

    args = request.json
    conf = args['config']
    #params = args['params']
    plot = args['plot']
    trace_name = args['trace_name']
    algorithm = args['algorithm']
    cache_size = args['cache_size']
    #params = [plot, trace_name, algorithm]

    app_id = args['id']

    print(conf, "get_y config")


    print(conf, " webapp input")
    print(args, " webapp input")
    print(app_id, " webapp input")
    # this is necessary because when sending the config over to the API, the " " in the config turn to ' ',
    # these have no sematic value in JSON, conf cannot be turned to JSON without this replacement 
    # the generate_graph_data function expects JSON for the config.
    #conf = conf.replace('\'', '\"')

    y_data, title = vsu.generate_y(conf, args, app_id)
    y_data = list(y_data)
    #print('graph gotten ++++++++++++++++++++++++++++++++++++++++++++++')
    #the response must be only 1 item. 

    print(type(y_data), " y axis: get_graph api output")
    print( title, " title: get_graph api output")

    #print(x[0:10], y[0:10], title, "GET GRAPH RESULTS") 
    #return str(0)
    conduit.current_status[app_id] = "data retrieved... rendering"
    return jsonify(ydata=str(y_data), graph_title=str(title) )



#get_time returns the time stamp array for a given trace only.
#this is to prevent repeated transferring of the same time data for each get_graph request

@app.route('/get_time', methods=['POST'])

def get_time():

    print("================================")
    print("Greetings from get_time")
    print("================================")

    #conf = request.form.get('config')
    '''conf = request.form['config']
    params = request.form['params']
    app_id = request.form['id']
    conf_response = jsonify(conf)'''

    args = request.json
    conf = args['config']
    trace_name = args['trace_name']
    app_id = args['id']

    print(conf, " webapp input")
    print(args, " webapp input")
    print(app_id, " webapp input")
    minio_get = Minio_Module.Minio_Module()
    over_time = svr.get_over_time_list(trace_name, minio_get, app_id)
    return jsonify(time=str(over_time))

#makes an access to a dictionary that holds the status for each request from the webapp 

@app.route('/status', methods=['POST'])

def get_graph_status():
    print("================================")
    print("Greetings from get_graph_status")
    print("================================")
    #app_id = request.form['id']
    app_id = request.json['id']
    print(app_id, " webapp input")
    print(conduit.current_status.get(app_id), " api output")
    try:
        stat = str(conduit.current_status[app_id])
        return stat
    except: return "waiting for updates..." 


#generates necesary data for heatmap
#output is a json file that holds:
#xs: a list of cache sizes designated by the user
#ys: a list of algorithms designated by the user
#zs: resulting rank data
@app.route('/get_heat', methods=['POST']) #allow POST requests
def get_heat():
    

    '''datasets =  request.form['dataset'].split(",")
    algos = request.form['algos'].split(",")
    cache_sizes = list(map(float, request.form['cache size'].split(",")))
    app_id = request.form['id']'''

    input_data = request.json

    algos = input_data['dataset']

    datasets =  input_data['dataset']
    algos = input_data['algos']
    cache_sizes = input_data['cache_sizes']
    app_id = input_data['id']

    xs, ys, zs = csvp.amended_dash_rank_heat_map(datasets, algos, cache_sizes, req_id = app_id)
    conduit.current_status[app_id] = "rendering heat map data..."

    print("================================")
    print("Greetings from get_heat")
    print("================================")

    print(datasets, " web app input")
    print(algos, " web app input")
    print(cache_sizes, " web app input")

    print( type(xs), xs , " api output")
    print(type(ys), ys, " api output")
    zs = zs.tolist()

    print(type(zs), zs , " api output")
    return jsonify(x_cache=xs, y_algs=ys, data = zs)

# generates all pairs of algorithms for each cache size for potential overlay comparison
# for example if a config specifies trace: ikki-1, cache size: [.005, .01, .1], algorithm: [arc, lfu, lru]
# it will pair arc with lfu, arc with lru and lfu with lru

@app.route('/get_permutations', methods=['POST'])
def get_permutations():

    print("================================")
    print("Greetings from get_permutation")
    print("================================")

    '''conf = request.form['config']
    graph_opt = request.form['graph_flag']'''

    conf = request.json['config']
    graph_opt = request.json['graph_flag']

    print(conf, "webapp input")
    print(type(conf))
    print(graph_opt, "webapp input")
    print(type(graph_opt))
    #conf = conf.replace('\'', '\"')
    #graph_opt = graph_opt.replace('\'','').strip('][').split(', ') 
    graph_params = vsu.config_permutation_gen(json.loads(conf), graph_opt)
    '''if graph_params == "Cache size for trace too small":
        return []'''
    print("\n", graph_params, "\nget permutations api output")
    print(graph_params, "========================================================================")
    return jsonify(graph_params)

@app.route('/get_graph_types', methods=['GET'])
def get_graph_types():
    #types = storage.get_graph_key()

    types = storage2.find_in_collection("graph_types", ["name","graph type key"])
    print(types[0])
    del types[0]["_id"]
    del types[0]["name"]

    return str(types[0])


@app.route('/get_conf_options', methods=['GET'])
def get_conf_options():

    print("================================")
    print("Greetings from get_conf_options")
    print("================================")

    #available_options = storage2.find_distinct_fields(collection_name, field)

    field = ['algorithm', 'cache_size', 'dataset']
    result = {}

    for f in field:
        distinct = storage2.find_distinct_fields('alg_runs', f)
        result[f] = distinct

    print(result, "api output")
    return result

#Returns all traces in specified datasets

@app.route('/get_trace_options', methods=['POST'])
def get_trace_options():

    print("================================")
    print("Greetings from get_trace_options")
    print("================================")
    print(request)
    ds=None
    request_params = request.json["dataset"]
    if request_params is not None:
        ds = request_params
        print(request_params, " webapp input")
    # find_in_collection('heat_workload', param=['dataset', 'FIU']) 
    available_records = storage2.find_in_collection('workload', param=["dataset", ds])
    available_traces = [ trace['trace name'] for trace in available_records]
    print(available_traces, " api output")
    return jsonify(available_traces)



if __name__ == "__main__":
    app.run(host='localhost', port=5000)



'''orig_stdout = sys.stdout
f = open('out.txt', 'w')
sys.stdout = f
sys.stdout = orig_stdout
f.close()'''


