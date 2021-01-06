# csv_plot readme:


===============
### plot_rank_heat_map(config):

retrieve csv heat data from minio and process it

input:
	
	config(JSON)

output:

	heat map graph in matplotlib

=================

===============
### amended_dash_rank_heat_map(custom_datasets, custom_algos, custom_sizes, req_id = None):

query mongo for the hit rate data of specified datasets, algorithms and cache sizes


input:
	
	custom datasets: list of strings corresponding to desired datasets
	custom algos: list of strings corresponding to desired algorithms
	custom sizes: list of strings corresponding to desire cache sizes
	req_id: request ID is used to identify the current request so that webapp can get status updates

output:

	x axis (list of all cache sizes)
	y axis (list of algorithm names)
	data (2d list where each entry corresponds to one algorithm of the y axis)

=================