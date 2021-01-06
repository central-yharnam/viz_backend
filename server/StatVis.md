# StatVis readme:

### StatVis is what calls matplotlib and what ultimately renders the plots

vis_data(self, graph_type, xlabel, ylabel, title, y_data, path, x_data = None , scale = None):

		Once all the data has been processed, it is send to vis_data and given the proper titling
		format and graphed accordingly. there are optional arguments for the y scale and the x data
		argument is for graphs that are over time. plotting is done in matplot lib

input: graph_type(string), xlabel(string), ylabel(string), title(string), y_data(list), path(string), x_data(list), scale(int)
output: graph with given data and labels

vis_data_multi(self, graph_type, xlabel, ylabel, title, y_data, path, x_data = None , scale = None):

	the only difference in input is that y_data is a list of lists. only 4 graphs will be overlayed at a time, any more than that will simply be ignored.

input: graph_type(string), xlabel(string), ylabel(string), title(string), y_data(2d list), path(string), x_data(list), scale(int)
output: graoh with given data overlayed



