#test bench for api

import requests
import conduit
import json
import sys
import time

heat = {'dataset': ['CloudCache', 'CloudPhysics', 'CloudVPS', 'FIU', 'MSR'], 
'algos': ['arc', 'arcalecar', 'cacheus', 'dlirs', 'lecar', 'lfu', 
'lirs', 'lirsalecar', 'lru'], 'cache_sizes': [0.0005, 0.001, 0.005, 0.05, 0.01, 0.1], 'id': '171ee852-8f81-4ff3-a9b4-541f7e5c43ad'}


conf = {"cache_sizes": [0.01], "algorithms": 
["lfu", "lru"], "dataset": ["FIU"], "traces": ["casa-110108-112108.4"]}

conf = json.dumps(conf)

graph = {'config': conf, 
'id': 'f4e17aae-1e0e-454a-aa24-99f5824d7851', 'algorithm': 'lfu', 
'cache_size': 1480, 'kwargs': None, 'plot': '-H', 'trace_name': 'casa-110108-112108.4'}


y_inp = {'config': {'cache_sizes': [0.01], 'algorithms': ['lru'], 'dataset': ['FIU'], 'traces': ['casa-110108-112108.4']}, 
'plot': '-H', 'trace_name': 'casa-110108-112108.4', 'algorithm': 'lru', 'cache_size': 0.01, 'id': 'd73c3a56-8696-42c6-900c-b79748fa4847'}
#what = json.dumps(graph)

perm = {'config': conf, 
'graph_flag': ['-H']}


dataset = {'dataset': "FIU"}


get_methods = ['/mongo_conf', '/get_graph_types', '/get_conf_options' ]

def test_get_method(backend_ip, path):

	output = requests.get(backend_ip + path)

	return output


def test_get_heat(backend_ip, inp):
	output = requests.post(backend_ip + '/get_heat', json=inp)

	return output

def test_get_graph(backend_ip, inp):
	output = requests.post(backend_ip + '/get_graph', json=inp)
	return output

def test_get_time(backend_ip, inp):
	output = requests.post(backend_ip + '/get_time', json=inp)
	return output

def test_get_y(backend_ip, inp):
	output = requests.post(backend_ip + '/get_y_axis', json=inp)
	return output

def test_get_trace_options(backend_ip, inp):
	output = requests.post(backend_ip + '/get_trace_options', json=inp)
	return output

# this function takes a config and an argument corresponding to the plot to graph.
# it returns data in the format passed to get_y

def test_get_permutation(backend_ip, inp):
	output = requests.post(backend_ip + '/get_permutations', json=inp)
	return output

def test_get_status(backend_ip, app_id):


	inp = {"id": app_id}
	stat = requests.post(backend_ip + '/status',json = inp)

	return stat

if __name__=='__main__': 
	print(sys.argv[1])

	#print("what")
	#test_get_method(sys.argv[1])


	be = sys.argv[1]

	for paths in get_methods:
		out = test_get_method(be, paths)
		print(paths)
		print(out.text)
		print("------------------------------------")

	heat_data = test_get_heat(be, heat)
	print("============== GET_HEAT API OUTPUT =================")
	print(heat_data.text)
	print('-----------------------')

	time.sleep(5)
	print("---------SLEPT FOR 5 SECONDS------------------")
	graph_data = test_get_graph(be, graph)

	print("============== GET_GRAPH API OUTPUT =================")

	print(graph_data.text[0:1000], "...")
	print("only displaying first 1000 characters, output is very long")

	print('-----------------------')


	time_data = test_get_time(be, graph)

	print("============== GET_TIME API OUTPUT =================")

	print(time_data.text[0:1000], "...")
	print("only displaying first 1000 characters, output is very long")

	print('-----------------------')


	y_data = test_get_y(be, y_inp)

	print("============== GET_Y API OUTPUT =================")

	print(y_data.text[0:1000], "...")
	print("only displaying first 1000 characters, output is very long")

	print('-----------------------')


	trace_options = test_get_trace_options(be, dataset)

	print("============== GET_TRACE_OPTIONS API OUTPUT =================")

	print(trace_options.text)

	print('-----------------------')


	conf_values = test_get_permutation(be, perm)

	print("============== GET_PERMUATAIONS API OUTPUT =================")

	print(conf_values.text)

	print('-----------------------')


	status_message = test_get_status(be, '1234')

	print("============== GET_STATUS API OUTPUT =================")
	print(status_message.text)

	print('-----------------------')