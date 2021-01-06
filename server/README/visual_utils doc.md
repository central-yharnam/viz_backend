# Visual utils readme:

==============================
the plots variable at the top holds a dictionary with the various plot flags available for graphing
along with a list of descriptors for these plots. there are used to tell the functions how to process
the plot data and what labels to send to matplotlib.

the general form for a dictionary entry is

the indices for the corresponding key's list are as follows
-plot[0] = 'trace' or 'algorithm', plots are either plots of trace data only or dependent on an algorithm.
-plot[1] = graph type, most graphs are line plots but some are different. this is needed for matplotlib processing
-plot[2] = minio id suffix. this is the suffix that is needed to find the data in the Minio store once the ID is gotten from
	   mongo.
-plot[3] = x axis labels
-plot[4] = y axis label
-plot[5] = graph title
-plot[6] = is it algorithm specific? there are some plots that are only valid for certain algorithms because a
	   certain internal algorithm variable is being tracked.


==============================



==============================

## list of valid flags
		 '-p': Access Pattern
         '-r': Reuse Distance Frequency Distribution'
         '-g': Frequency Distribution of Accesses
         '-H': Hit Rate
         '-P': Pollution
         '-m': Miss Rate
         '-l': Weight of LRU
         '-w': Value of Arc P
         '-d': Dlirs Stack Size
         '-y': Weight of LRU
         '-x': Cacheus Learning Rate
         '-z': Cacheus SR Stack Size


### process_histogram(flag, array):
input

	flag: a string, either "-g" for access frequency histogram or "-r" for reuse distance
	array: a list to be processed by the function

output:

	there are 2 different kinds of histograms and they need to be processed differently. there is the access frequency plot and the reuse distance histogram. 
		if it is the access frequency histogram 
		- a list of x values, corresponds to the number of times an LBA was accessed. 
		- a list of y values to plot, number of times an LBA was accessed N times
		for example: X value 2 means LBAs accessed twice, and Y value 10 means there were 10 LBAs accessed twice.
		- number of unique requests in the trace
		if it is reuse distribution:
		- list of x values
		- list of y values 

============================

====================================================
### reuse_distrib(reuse_array): 
calculates reuse distances for each LBA and returns an array where the indices correspond to the reuse distances and the values held in the index are how many 
for example, index 1 holds how many reuse distances of 1 there were in the trace and so on
input:

	reuse_array: a dictionary where key is LBA and value is a list of all the times that LBA was called. This is used to calculate all reuse distances

output:
	
		reuse_result: a list where the indices correspond to reuse distance and value held is the number of reuse distances

====================================================

====================================================
### visualize_data(flag, config, y_scale=None): 
this is one of the major functions, this calls many other functions
in the folders, checks if things exists, gets pertinent data, processes it if necessary and then plots it.
y_scale is an optional argument that sets y axis scale range on the graph from 0 to whatever value is input
input: 
	
	flag (string of a valid flag), config (JSON of config), y_scale (optional parameter that sets the y axis scale for display)

output:

	resulting matplotlib plots are saved as images to a folder
	
====================================================

====================================================
### config_permutation_gen(config, flags): 
checks if the cache size is large enough and then outputs a list where entries are organized as such 

{"plot":flag, "trace_name":trace, "algorithm":None, "cache_size":None, "kwargs": None}

utility for organizing data for webapp
input: 

	config (JSON of config), flags(list of strings that are valid flags)

output:

	params: list of dictionary entries with above format
====================================================

====================================================
### s_generate_graph_data(config, params, app_id): 
downloads data if it exists in the database, generates it if not.

Note that the cache size value here is different than the cache sizes a user can specify in the webapp menu. This is because the number of cache blocks available when a simulation is run is determined as: 

(number of unique accesses * user defined cache size)

input:

	- config(JSON of config)
	- params(a dictionary with keys 'plot', 'trace_name', 'algorithm', 'cache_size')
	- app id (unique string for status updates for webapp)
	

output:

	- x axis (list)
	- y axis(list) 
	- title(string)

====================================================

====================================================
### generate_y(config, params, app_id): 
downloads or generates y axis data and title.

** this function should only be used for over time graphs, there is no additional processing for the histograms **


input:

	- config(JSON of config)
	- params(a list of parameters of the form [plot, trace_name, algorithm])
	- app id (unique string for status updates for webapp)

output:

	- y axis(list) 
	- title(string)
====================================================

====================================================

### visualize_head_to_head(config, flag, y_scale = None): 

this method is used in visualapiEX to plot the fill comparison graph for hit rate. For the webapp however, this is not called.
the config has an output path that specifies where the output images should be saved to.

input:
		
	-config: JSON of config
	-flag: string of valid flag (any over time plot is valid for head to head visualization)
	-y_scale: value > 0 to set the y axis scale for the plots
	
output:	

	-images of plots overlayed and filled saved to a folder
====================================================


====================================================
### gen_all_pairs(array)

this is a helper function for visualize head to head. it generates all pairs of algorithms for overlay plotting


input:
		
	- array (list of algorithms to plot)
	
output:	

	- 2d array (list where each entry is a list with 2 elements corresponding to all pairs)
====================================================

====================================================

====================================================

====================================================

### visualize_data_multi(flag, config, y_scale = None)

quite similar to visualize_data except that multiple graphs are superimposed on each other.
it superimposes the first 4 cache sizes and then ignores the rest.


input:
		
	-config: JSON of config
	-flag: string of valid flag (any over time plot is valid for head to head visualization)
	-y_scale: value > 0 to set the y axis scale for the plots
	
output:	

	-images of plots overlayed and filled saved to a folder

====================================================
