StatVis is a class with two functions:


vis_data(self, graph_type, xlabel, ylabel, title, y_data, path, x_data = None , scale = None):
		Once all the data has been processed, it is send to vis_data and given the proper titling
		format and graphed accordingly. there are optional arguments for the y scale and the x data
		argument is for graphs that are over time. plotting is done in matplot lib


vis_data_multi(self, graph_type, xlabel, ylabel, title, y_data, path, x_data = None , scale = None):
		the only difference here is that multiple graphs are plotted at once for comparison.


