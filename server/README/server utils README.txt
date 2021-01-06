all of the methods that talk to the mongo and minio servers used in server utils


mongo_new_paths(config): makes a query to mongo for all workload traces in the config file passed as an argument

printMongoResults(trace_name): makes a query to mongo for a trace and prints results if found, else prints which trace would not be found

mongo_new_alg_runs(config): makes a query to mongo for all algorithms and cache sizes in config, if the trace is found, the resulting data 			    	    is printed. if the trace is not found the algorithm and cache size is run then the data is printed.
 		  	    

MongoDB holds all the 'small' data, such as overall hitrate and number of requests. Minio holds all of the data to be graphed, like the list of time stamps and list of hit rates at each time interval. 

request_alg_run_plot_data(trace_name, algorithm, cache_size, plot, minio_get): given a trace name, algorithm and cache size the trace key
									       is found in mongo and then the plot is retrieved from Minio.
									       the filenames in minio follow the formula of mongoID-flag
									       for example 234ez67-rq for the requests over time graph 									       data. this is a helper method for mongo get plot data

mongo_get_alg_run_plot_data(config, plot, trace_name, 
			algorithm, cache_size, minio_get): this method checks if the current combination of trace, algorithm and cache 						           		   size is in the database.if it is, it makes a request to minio. if not, it runs 							   	   the algorithm on the trace with given cache size and then makes a request for 							   the plot data. 

mongo_get_trace_run_plot_data(trace_name, plot, minio_get): this method is for getting trace data from minio.
							    all that is needed for trace data is the name of the trace and the desired 								 	    plot. 
						            if no trace data is found, it is generated.
							    ********This is different than mongo_get_alg_run_plot because there is a 							    				    difference graphs that are contingent on the Algorithm and those that only
							    need the trace data.

normalize_real_time(time_stamps): a utility function to process the list of timestamps generated when  the trace is processed. they are normalized to start
				  at 0.

get_over_time_list(trace_name, minio_get): makes a request to minio for the time stamp data for a given trace. The MongoID for the trace is found and used
					   to access the corresponding data in minio. minio_get is passed because the contact minio a class instance is 					   needed.
mongo_get_unique(trace_name): get number of unique requests in a trace. this is necessary to calculate the number of cache slots. the cache size input
			      is a percentage > 0 and <= 1 , the cache size is determined by (# of uniques * cache size)

as_to_Database(trace, algname, cache_size, ios, hits, hit_rate, misses, pollution, f_eviction_rate, f_eviction_total, 
hit_ot, miss_ot, pol_ot, minio_only,dlirs_HIR_s = None, lecar_lru = None , arc_p = None, 
cacheus_learning_rate = None, cacheus_lru = None, cacheus_q = None): pushes all Algorithm Statistics to mongo and minio. This data is specific to a 
								     trace, cache size and algorithm. 

as_minio_confirm(traceId, traceName, algname, cache_size): confirm that the data was indeed uploaded to minio.

s_to_database(trace, num_req, num_unique, num_reuse, 
num_writes, num_requests, req, histogram, reuse_distance, time_stamp, minio_only): upload trace data to the database. After the first time the 
										   trace is processed there should be no more s to database calls.

s_minio_confirm(traceId, traceName): confirm the data was successfully uploaded to minio.


these functions arent used anymore because the user can't upload a custom config onto the server anymore. 
catch_config_errors(config): a function to catch input errors with the config: a cache size that's too large or invalid algorithms.
catch_json_errors(conf): a function to catch json formatting errors
			     


											