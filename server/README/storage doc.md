# storage readme:

## the methods in storage all contact MongoDB
## contact to MongoDB is done through the pymongo interface

=======================================================
### store_workload(name, total, unique, reuses, writes, time): 
upload a new item to the workload collection with the specified information, inputs are the fields for the workload in mongo
input:

	- name (string)
	- total(int)
	- unique(int)
	- reuses(int)
	- writes(int)
	- time(int)


=======================================================

=======================================================
### workload_confirmed (traceName, request = None, requestFrequency = None, reuseDistance = None, time = None): 

input:

changes the information in the database with the timestamp of when the data for specified trace was confirmed to have been uploaded to minio. 
this function does not do any checking itself. when the function is called with an optional argument as True then it updates the corresponding field in mongoDB.

	traceName (string)
	request (boolean, optional)
	requestFrequency (boolean, optional)
	reuseDistance (boolean, optional)
	time (boolean, optional)



=======================================================

=======================================================
### trace_run_confirmed(traceId, hit_rate = None, miss_rate = None, pollution = None, dlirs = None, lecar = None, arc = None, cacheus = None): 

changes the information in the database with the timestamp of when data for the trace was confirmed to have been uploaded to minio 

	
	fields changed in mongo db are: 
	hit rate array
	miss rate array
	pollution array
	dlirs stack size
	parameter p in arc
	Size of the resident HIR for DLIRS
	The weights of SR-LRU (scan resistant LRU) for Cacheus
	Learning rate for Cacheus
	Size of SR stack for Caceus

input: 

	traceId (string)
	hit_rate (boolean)
	miss_rate (boolean)
	pollution (boolean)
	dlirs (boolean)
	lecar (boolean)
	arc (boolean)
	cacheus (boolean)

=======================================================

=======================================================
### new_store_alg(ios, hits, hit_rate, misses, pollution, evRate, evcs, alg_name, cache_size, t_name): 

stores a new algorithm in the trace_runs collection with the fields specified.
evRate and evcs should be ignored, we are not looking at evictions anymore.
the trace_runs collection holds all data for traces being run with a particular cache size and algorithm. 

input: 

	- ios (int) 
	- hits(int) 
	- hit_rate(float) 
	- misses(int) 
	- evRate(unused) 
	- evcs (unused) 
	- alg_name(string) 
	- cache_size (float in interval (0.0, 1.0] 
	- t_name (string))
	
	
=======================================================
=======================================================
### insert_config(config, name): 

at the moment, inserting a config should not be possible through the web app. however,
you send a config file (which is in JSON format) to mongo with a given name and if the name is 
not in mongodb it processes the config and then inserts it to the config collection in mongo.

input: 

		- config(JSON) 
		- name(string)

	

=======================================================
=======================================================
### get_all_configs(): 
output:

	yields all configs in the config collection, configs are returned in JSON format
=======================================================

=======================================================
### find_trace_run(trace_name, algorithm, cache_size): 
input: 

		trace_name(string), algorithm(string), cache_size(float in interval (0.0, 1.0])

output: 
	
	False if no entry was found, JSON of trace object stored in mongo if found
	look for an entry in the trace_runs collection that has the specified trace name, algorithm and cache size.
=======================================================

=======================================================
### find_trace_run_id(trace_name, algorithm, cache_size): 

	input: trace_name(string), algorithm(string), cache_size(float in interval (0.0, 1.0])
	output: False if no entry was found, id for trace results if found

=======================================================

=======================================================

### find_trace(trace_name): 
	input: trace_name (string)
	output: False if trace_name is not found, entry in mongo if found.

=======================================================

=======================================================
### find_id(trace_name): find Mongo ObjectID of object with a given trace name in the workload collection.

	input: trace_name(string)
	output: False if trace_name is not found, a string that is the trace entry's ID in Mongo if found.

=======================================================

### find_in_collection(collection_name, param=None): 
input: 

	- collection_name(string), 
	- param=['field','value']

output: 
	
	- list containing all mongo objects that have that value in the given field.

param is an optional argument, if it is not given any value, find_in_collection will simply return all objects.

for example, collection_name = 'alg_runs' (which holds all the results of the traces run with a certain alg and cache size)
param = ['dataset', 'fiu'] in this case I want to search the alg_runs collect for every entry who's dataset field is FIU.
find_in_collection('alg_runs') would output a list of all entries in the alg_runs collection.


### distinct_fields_available(): 

finds all distinct algorithms, cache sizes and datasets in the algruns collection. this is for the config builder in the webapp. 

output:

	- result: a dictionary with keys 'algorithm', 'cache_size', 'dataset' each key has a value which is a list of strings of all distinct values in mongo

