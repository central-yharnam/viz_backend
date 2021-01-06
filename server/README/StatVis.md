# StatVis readme:

### StatVis is what calls matplotlib and what ultimately renders the plots

================================================
#### vis_data(self, graph_type, xlabel, ylabel, title, y_data, path, x_data = None , scale = None):

Once all the data has been processed, it is send to vis_data and given the proper titling
format and graphed accordingly. there are optional arguments for the y scale and the x data
argument is for graphs that are over time. plotting is done in matplot lib

x data is an optional argument since not all graphs are over time graphs
scale is an optional argument that takes an integer value > 0 that sets the Y axis scale in the resulting graph

input: 
		
		- graph_type(string) 
		- xlabel(string) 
		- ylabel(string) 
		- title(string) 
		- y_data(list) 
		- path(string) 
		- x_data(list) 
		- scale(int)

output: 

	graph with given data and labels are saved as images to path specified in path argument

================================================

================================================

#### vis_data_multi(self, graph_type, xlabel, ylabel, title, y_data, multi_labels, path, x_data = None, scale = None, fill=None):

the only difference in input is that y_data is a list of lists and fill is an extra optional argument. only 4 graphs can be overlayed at a time, any more than that will simply be ignored.

x data is an optional argument since not all graphs are over time graphs
scale is an optional argument that takes an integer value > 0 that sets the Y axis scale in the resulting graph
fill is an optional argument that fills the inbetween space of 2 graphs


input:
		
		- graph_type(string), 
		- xlabel(string), 
		- ylabel(string), 
		- title(string), 
		- y_data(list), 
		- path(string), 
		- x_data(list), 
		- scale(int)
		- fill




output: 
	
	graph with given data and labels are saved as images to path specified in path argument

===============================================

