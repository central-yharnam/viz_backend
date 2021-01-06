# Caching Algorithm Visualizer Webapp API
===========
**This is the documentation for the webapp api. Before the functions are introduced, the config must be described.**
**The config is a JSON document that specifies what to graph. Many functions in the API take a config as an argument**

========

example config:


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

========

# API functions:


================================================================

### **get_graph**:
#### *POST method*
#### *route: /get_graph*

**list of valid strings for "plot" field**: 
"-p": access pattern
"-H": hit rate over time
"-P": pollution
"-g": histogram, generates a bar graph of how many times each LBA is called
"-m": miss rate over time
"-d": Generates a graph of the size of the dlirs HIR stack over time
"-l": Generates a graph of the lecar lru value over time

"-w": Generates a graph of the arc p value over time

"-x": Generates a graph of the cacheus learning rate value over time
"-y": Generates a graph of the cacheus lru value over time

"-z": Generates a graph of the cacheus lru value over time

"-r": Generates a graph of reuse distances

"-c": generate heatmap from csv documents based on rank

"-v": generate all pairs between algorithms specified in config and compare hitrates between the two for each cache size and trace


**JSON input**:

    {
    "config": {JSON with config data, see example above}
    "plot": a string with the plot
    "trace_name": a string with the trace name
    "algorithm": a string with the desired algorithm
    "cache_size": floating point value > 0 and less than or equal to 1
    "id": unique string to identify this get graph request
    }

**JSON output**:

    {
    "xaxis":[list of x values]
    "yaxis":[list of y values]
    "res_title":string with title
    }

====================================================

### **get_graph_status**:
#### *POST method*
#### *route: /status*

**JSON input**:

    {
    "id": unique string to identify this get graph request
    }

**JSON output**:

    {
    "status": string with current status
    }

====================================================

====================================================
### **get_time**:
#### *POST method*
#### *route: /get_time*

**JSON input**:

    {
    "config": {JSON with config data, see example above}
    "trace_name": a string with the trace name
    }

**JSON output**:

    {
    "time":[list of x values the represent the time stamps]
    }

====================================================


====================================================
### **get_y_axis**:
#### *POST method*
#### *route: /get_y_axis*

**JSON input**:

    {
    "config": {JSON with config data, see example above}
    "plot": a string with the plot
    "trace_name": a string with the trace name
    "algorithm": a string with the desired algorithm
    "cache_size": floating point value > 0 and less than or equal to 1
    "id": unique string to identify this get graph request
    }

**JSON output**:

    {
    "ydata":[list of y values for specified alg run]
    "graph_title": string that is the title of the graph
    }

====================================================


====================================================

### **get_heat**:
#### *POST method*
#### *route: /get_heat*

**valid dataset values**: "FIU", "CloudCache", "MSR", "CloudPhysics", "CloudVPS"
**valid algorithm values**: "arc","arcalecar", "cacheus","dlirs", "lecar", "lfu", "lirs", "lru"

**JSON input**:

    {
    "dataset": [list of desired datasets from the above list]
    "algorithms": [list of desired algorithms from the above list]
    "cache_size":[list of values greater than 0.0 and less than or equal to 1.0]
    }

**JSON output**:

    {
    "x_cache":[list of cache sizes]
    "y_algs": [list of algorithms]
    "data":[2d list where "data"[0] corresponds to the list of result values for the first data set and so on] 
    }

====================================================

====================================================

### **get_permutation**:
#### *POST method*
#### *route: /get_permutations*

#### checks if the cache size is large enough and then outputs a list where entries are organized as such 

#### {"plot":flag, "trace_name":trace, "algorithm":None, "cache_size":None, "kwargs": None}

**valid plots**: -H (hit rate over time), -m (miss rate over time), -P (pollution over time)

**JSON input**:
    {
    "config": {JSON of config, example at top}
    "graph_flag": [list of plots to compare]
    }

**JSON output**:

    {
    "traces": [list dictionaries]
    }

====================================================

====================================================

### **get_trace_options**:
#### *POST method*
#### *route: /get_trace_options*

**possible dataset values**: "FIU", "CloudCache", "MSR", "CloudPhysics", "CloudVPS"

**JSON input**:

    {
    "dataset": string of one of the 5 possible datasets
    }

**JSON output**:

    {
    "traces": list of all traces in specified dataset
    }

====================================================
==
====================================================

### **get_conf_options**:
#### *GET method*
#### *route: /get_conf_options*

**JSON output**:
Returns a string of a dictionary with all unique values in Mongo that are valid to choose as graphing parameters: cache sizes, algorithms and datasets

    {
    "algorithm": [list of valid algorithms]
    "cache_size": [list of valid cache sizes]
    "dataset":[list of valid datasets]
    }

====================================================
=
====================================================

### **mongo_configs**:
#### *GET method*
#### *route: /mongo_conf*

**JSON output**:
list of all configs where keys correspond to index of config

    {"0":first config
    "1": second config
    ...}

====================================================