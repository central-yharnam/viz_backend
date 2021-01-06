visualapiEX
===========

dependencies: pandas, numpy, Matplotlib, Boto3, pymongo, dnspython, Flask, Dash, colorama

this is the original version of the graphing program. it is run from the console

to run the program, a command like this must be written into the console.

"python visualapiEX.py example.config -flag"

if no arguments are passed, it will output the help menu.

methods called:

serv.mongo_new_paths(config) - makes a query to mongo for all workload traces in the config file passed as an argument. 
			       it returns a list of the traces that have not been processed in the config.
singleTraceGen(traces) - takes a list of traces and processes them, then uploads the data to mongo and minio.

serv.mongo_new_alg_runs(config) - makes a query to mongo for all algorithms and cache sizes in config 
		             if the trace is found, the resulting data is printed. 
			     if the trace is not found the algorithm and cache size is run 
 		  	     then the data is printed 

vu.visualize_data('-flag', config) - this is the main loop that gets data, processes it and then plots it. 
vu.visualize_head_to_head(config, flag, y_scale = None) - right now it plots all permutations of pairs of hit rate plots for each 
							  algorithm on a given trace and cache size. But it can be modified to do the same
							  for any other flag that has time as the X axis.

alg_check(config, algorithm) - checks if the algorithm specified with the flag is specified in the config. This is only for graphing
			       certain graphs that are dependent on a particular algorithm. For example there are variables for
			       cacheus that are tracked, however if no cacheus algorithm is specified in the config the command is invalid.

list of flags:

-s: Generates the statistics for the traces specified in the config. This is data that is specific to the TRACE ONLY, no algorithms
    are run at this stage. 
    Data generated is:
	 number of requests 
	 number of uniques 
	 number of reuses 
	 number of writes 
	 list of requests over time
	 list of time stamps (this is the X axis for many graphs)
	 list of the number of times a reuse distance has been counted
	 list of individual LBAs and how many times they have been called so far
*Because of the way that cache size is generated (as a percentage of the number of uniques) it is always necessary to run this first

-a: Generates the alg statistics for the traces specified in the config. The data here now runs all algorithms and cache sizes specified
    in the config.
    Data generated is:

    average pollution
    number of misses
    number of ios
    hit rate at each request
    pollution at each request
    miss rate at each request
    ######## these are algorithm specific stats and are not generated every time ########
    LeCaR: the weight of LRU and LFU vs Time

    ARC: parameter p vs Time

    DLIRS: Size of the resident HIR (High Interference Recency) stack vs Time

    Cacheus :

    	The weights of SR-LRU (scan resistant LRU) vs Time. 
    	Learning rate vs Time.
    	Size of SR stack vs Time 
-H: Graph Hit rate vs Time for each trace, algorithm and cache size specified in the config.
-m: Generates a graph for the miss rate curve
-p: Graph access pattern over time. Each request is given a number, the first LBA is mapped to 1 the second to 2 and so on. 
    at time X (axis), LBA Y (axis) is requested and that is what is plotted in the graph.  
-P: Graph pollution over time. cache pollution is said to occur when prefetched data replaces more useful data (demand-paged or prefetched)     from the cache.
-r:  Generates a graph of reuse distances. i.e How many times was a reuse distance of 5 seen? and so on.
-g:  Generates a bar graph of how many times each LBA is called. (It's actually a line plot because the bar graph just freezes with large        data)
-d: Generates a graph of the size of the dlirs HIR stack
-l: Generates a graph of the lecar lru value over time
-w: Generates a graph of the arc p value over time
-x: Generates a graph of the cacheus learning rate value
-y: Generates a graph of the cacheus lru value over time
-z: Generates a graph of the cacheus lru value over time
-r: Generates a graph of reuse distances 
-t: --test 
-c: generate heatmap from csv documents based on rank

-v:  generate all pairs between algorithms specified in
     config and compare hitrates between the two for each
     cache size and trace. 

