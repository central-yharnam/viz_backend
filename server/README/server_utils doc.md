# server_utils readme:


===============
### mongo_new_paths(config):

this was used in the console utility to check if a trace had been run before 

input: 

	config(JSON)

output: 

	returns a list of traces that are not in MongoDB yet

=================

=================
### printMongoResults(trace_name):


input: 
	
	trace_name(string)
output: 

	prints workload data for trace, trace name, number of requests, number of unique accesses, number of reuses, number of writes, and time
	if trace is not found, return False


=============

============
### mongo_new_alg_runs(config):

parses config and goes through all cache sizes, algorithms and traces. if a trace, cache size and algorithm combination is not found, it is processed and then the results are printed.
if it is found, the results are printed

input: 
		
	config(JSON)

output: 

	print data for all trace-cache_size_algorithm combinations 

============

============
### request_alg_run_plot_data(trace_name, algorithm, cache_size, plot, minio_get):
helper method for mongo_get_alg_run_plot_data

input: 

	trace name(string)
	algorithm(string)
	cache size(float)
	plot(string) 
	minio_get(instance of minio module)

example input: request_alg_run_plot_data("homes-sample.blkparse", "arc", .02, '-hit_rate')

output: 
		
		if retrieval from minio is successful it will write a temporary file to disk and returns the filename so
		matploblib can access it. 
		if not, it will return False.

============

============
### mongo_get_alg_run_plot_data(config, plot, trace_name, algorithm, cache_size, minio_get):

processes or returns the filename for requested minio data

input: 
	
	config(JSON)
	plot(string)
	trace_name (string)
	algorithm(string)
	cache_size(float)
	minio_get(instance of minio module)

output: 

	checks if the trace-algorithm-cache_size is in the database, 
	if it is, it is retrieved from minio with request_alg_run_plot, the filename is returned. 
	if not, it is processed, saved as an NPZ and uploaded to minio, then filename is returned.

============

============
### normalize_real_time(time_stamps):

a utility function to process the list of timestamps generated when  the trace is processed. they are normalized to start at 0.

input: 
	
	time_stamps(list of time stamp values)

output: 

	new timestamp list starting at 0

=========

=========
### get_over_time_list(trace_name, minio_get):

makes a request to minio for the time stamp data for a given trace. 

input: 

	trace_name(string), minio_get(instance of minio module)
output: 

	timestamp data as a list

=======

======
### mongo_get_unique(trace_name):

get number of unique LBA requests for a give trace

input: 

	trace_name(string)
output: 

	uniques(int)

======


=====
### as_to_Database
### (trace, algname, cache_size, ios, hits, hit_rate, misses, pollution, f_eviction_rate, f_eviction_total, 
### hit_ot, miss_ot, pol_ot, minio_only,dlirs_HIR_s = None, lecar_lru = None , arc_p = None, 
### cacheus_learning_rate = None, cacheus_lru = None, cacheus_q = None)

pushes all algorithm statistics to mongo trace_runs collection and minio. This data is specific to a trace, cache size and algorithm. 

input: 
	
	trace(string) 
	algname(string)
	cache_size(float) 
	ios(int)
	hits(int)
	hit_rate(float)
	misses(int)
	pollution(int)
	f_eviction_rate
	f_eviction_total
	hit_ot(list)
	miss_ot(list)
	pol_ot(list)
	minio_only(boolean)
	optional arguments dlirs_HIR_s, lecar_lru , arc_p , cacheus_learning_rate , cacheus_lru , cacheus_q  are all lists
output: 
	
	mongo_id(string)


====

====
### as_minio_confirm(traceId, traceName, algname, cache_size):

confirm that the data was indeed uploaded to minio.

input: 
	
	traceId(string)
	traceName(string) 
	algname(string)
	cache_size(float)
output: 
	
	return False if there was an error uploading something, return True if confirmed

====

====

====


====

### s_to_database(trace, num_req, num_unique, num_reuse, num_writes, num_requests, req, histogram, reuse_distance, time_stamp, minio_only):

saves NPZ files to disk that are then uploade to minio as well as results data that is sent to MongoDB

input: 

	trace(string)
	num_req(int)
	num_unique(int) 
	num_reuse(int) 
	num_writes(int) 
	num_requests(int) 
	req(list)
	histogram(list) 
	reuse_distance(list) 
	time_stamp(list)
	minio_only(boolean)

output:

	mongoID (string)
====


====
### s_minio_confirm(traceId, traceName):

input: 
		
	traceId(string)
	traceName(string)
output: 

	return True if workload data was confirmed to be found in db, 
	False if there was an error

====


====

### catch_config_errors(config):

checks for input errors in config

input: 
	
	config (JSON)
output: 

	returns 2 lists of incorrect inputs, invalid_algs and invalid cache size
	if everything is correct 2 empty lists are returned instead

====


====

### catch_json_errors(conf):

catches json errors in case the config was formatted incorrectly

input:
	
	config (JSON)
output: 

	False is there is a JSON decode error, else return config

====