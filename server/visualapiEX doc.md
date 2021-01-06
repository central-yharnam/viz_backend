#visualapiEX documentation
===========

###**dependencies**: pandas, numpy, matplotlib, Boto3, pymongo, dnspython, Flask, Dash, colorama

###this is the original version of the graphing program. it is run from the console

###to run the program, a command like this must be written into the console.

###"python visualapiEX.py example.config -flag"

###example config:


    {"cache_sizes": [0.001, 0.01],
    
    "traces": ["homes-110108-112108.19.blkparse", "./homes-sample.blkparse"],
    
    "algorithms": ["lecar", "dlirs", "arc", "cacheus"],
    "alecar6":{"learning_rate": [0.1, 0.2]},
    "lecar": {
        "learning_rate": [0.1]
    }}

    

===

**Traces, algorithms and cache_sizes are necessary fields.**
**traces**: takes a list of trace names, trace names are *strings*
**algorithms**: takes a list of algorithms to run tests with, algorithm names are *strings*

- valid algorithms: *arc, alecar6, arcalecar, cacheus, dlirs, lecar, lfu, lirs, lru*

**cache_sizes**: takes a list of *floating point values* in the interval (0.0 and 1.0]. The actual cache size that is used when running the algorithm and cache size is determined by 

---

#### (cache size value \* number of unique requests in trace) 
#### For example: (.01 \* 1000) = 10 cache slots

---

========



**Certain algorithms have optional arguments that can be specified in the config**

**algorithms and their acceptable optional arguments**:

- alecar6: "learning_rate
- cacheus: "learning_rate"
- lecar:"learning_rate"

learning_rate takes a list of *floating point values* in the interval (0.0, 1.0]
JSON does not parse floating point numbers that do not start with a 0. For example .01 as input will throw an error, it must be written 0.01.

###if no arguments are passed in the console,visualapiEX will output the help menu.

###**list of flags and descriptions**:

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

**Because of the way that cache size is generated (as a percentage of the number of uniques) it is always necessary to run this first**
**the values that are only 1 number are stored in the mongo database, the lists are compressed and stored in minio**

    -a: Generates the alg statistics for the traces specified in the config. The data here now runs all algorithms and cache sizes specified
        in the config.
        Data generated is:
            - average pollution
            - number of misses
            - number of ios
            - hit rate at each request
            - pollution at each request
            - miss rate at each request
            ##the following are algorithm specific stats and are not generated every time ##
            LeCaR: the weight of LRU and LFU vs Time
            ARC: parameter p vs Time
            DLIRS: Size of the resident HIR (High Interference Recency) stack vs Time
            Cacheus :
                - The weights of SR-LRU (scan resistant LRU) vs Time. 
                - Learning rate vs Time.
                - Size of SR stack vs Time 
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

##methods called:

###serv.mongo_new_paths(config): 
    makes a query to mongo for all workload traces in the config file passed as an argument. 
    it returns a list of the traces that have not been processed in the config.

###singleTraceGen(traces):
    takes a list of traces and processes them, then uploads the data to mongo and minio. returns a string that is the database ID for that trace data.

###serv.mongo_new_alg_runs(config):
    makes a query to mongo for all algorithms and cache sizes in config 
    if the trace is found, the resulting data is printed. 
    if the trace is not found the algorithm and cache size is processed 
    then the resulting data is printed 
    if there is an error with the processing of the data specified, the function returns false

###vu.visualize_data('-flag', config):
    this is the main loop that gets data, processes it and then plots it
    displays the desired plot in matplotlib

###vu.visualize_head_to_head(config, flag, y_scale = None)
    right now it plots all permutations of pairs of hit rate plots for each 
    algorithm on a given trace and cache size. But it can take any flag that is an over time graph 
    and return a set of overlayed plots where the differences are filled in with color

###alg_check(config, algorithm) - 
    checks if the algorithm specified with the flag is specified in the config. This is only for graphing
    certain graphs that are dependent on a particular algorithm. 
    -d: Generates a graph of the size of the dlirs HIR stack
    -l: Generates a graph of the lecar lru value over time
    -w: Generates a graph of the arc p value over time
    -x: Generates a graph of the cacheus learning rate value
    -y: Generates a graph of the cacheus lru value over time
    -z: Generates a graph of the cacheus lru value over time
    -r: Generates a graph of reuse distances 
    returns an error if a flag is specified that is not in the config.
    for example, if -d is specified in the console input but dlirs is not specified in the config, it will return an error