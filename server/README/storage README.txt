these are all the methods that contact MongoDB
contact to MongoDB is done through the pymongo interface

store_workload(name, total, unique, reuses, writes, time): upload a new item to the workload collection with 
							   the specified information. all of the arguments should be ints
							   except for the name.

workload_confirmed
(traceName, request = None, 
requestFrequency = None, 
reuseDistance = None, time = None): changes the information in the database with the timestamp of when a certain dataset
				    was confirmed to have been uploaded to minio. 

				    datasets checked for are: 
					request array (this is for the -p graph) access pattern
					request frequency (this is for -g graph) histogram
					reuse distance (this is for -r graph) reuse distance
					time (this is the x axis for many graphs) 

																	
trace_run_confirmed(traceId, hit_rate = None, miss_rate = None, 
pollution = None, dlirs = None, 
lecar = None, arc = None, cacheus = None): changes the information in the database with the timestamp of when a certain dataset
				    was confirmed to have been uploaded to minio.  
				all of these have time as X axis
				datasets checked for are: 
					hit rate array
					miss rate array
					pollution array
					dlirs stack size
					parameter p in arc
					Size of the resident HIR for DLIRS
					The weights of SR-LRU (scan resistant LRU) for Cacheus
					Learning rate for Cacheus
					Size of SR stack for Caceus

new_store_alg(ios, hits, hit_rate, misses, pollution, 
evRate, evcs, alg_name, cache_size, t_name): stores a new algorithm in the trace_runs collection with the fields specified.
					     evRate and evcs should be ignored, we are not looking at evictions anymore.
					     so what is stored is hit rate at the end, miss rate at the end, pollution at the end
					     the algorithm name, the cache size and the trace name.

insert_config(config, name): at the moment, inserting a config should not be possible through the web app. however,
			     you send a config file (which is in JSON format) to mongo with a given name and if the name is not in 			     		     mongodb it processes the config and the inserts it to the config collection in mongo.

get_all_configs(): returns all configs in the config collection


find_trace_run(trace_name, algorithm, cache_size): look for an entry in the trace_runs collection that has the specified trace name, 						   algorithm and cache size.

find_trace_run_id(trace_name, algorithm, cache_size): return mongo ID of trace with specified algorithm and cache size

find_trace(trace_name): return entry in workload collection for specified trace name



find_id(trace_name): find Mongo ObjectID of object with a given trace name.

find_in_collection(collection_name, param=None): search a given collection for specified value in a field. This is quite general
						 and can be applied to any collection as long as you know the name.
						 collection_name is a string and param is a list with two strings.
						 for example, collection_name = 'alg_runs' (which holds all the results of the traces run 						 	 with a certain alg and cache size)
						 param = ['dataset', 'fiu'] 
						 in this case I want to search the alg_runs collect for every entry who's dataset field
						 is FIU.


distinct_fields_available(): finds all distinct algorithms, cache sizes and datasets in the algruns collection. this is for the config 			     builder. 


			     
