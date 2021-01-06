import numpy as np
import seaborn as sb
import pandas as pd
import seaborn as sns
sns.set(color_codes=True)

from scipy import stats
import matplotlib.pyplot as plt
import os.path as path
import pretty
from StatGen import generateTraceNames
import storage
import storage2
import Minio_Module
import n_rank as nr
import conduit


plt.style.use('seaborn-whitegrid')


def plot_rank_heat_map(config):

	for paths in config['rank']:
		for rank_csv in generateTraceNames(paths):
			toMinio = Minio_Module.Minio_Module()
			cur_csv = storage.find_csv_run(rank_csv)
			cur_id = str(cur_csv.get("_id"))
			success = toMinio.retrieve(cur_id + '_csv_rank' +'.zip', cur_id)
			#csv_id = find_csv_run(rank_csv)
			if success:

				df_all = pd.read_csv(cur_id + '_csv_rank' +'.zip')
				df_all.columns = ['traces', 'trace_name', 'algo', 'hits', 'misses', 'writes', 'filters', 
				                        'size','cache_size', 'requestcounter', 'hit_rate', 'time',
				                        'dataset', 'rank']
				# df_all.drop(['trace_name', 'hits', 'misses', 'writes', 'filters', 'size', 'requestcounter',
				#              'time'], axis=1)
				#['traces','algo','cache_size','hit_rate', 'dataset', 'rank']


				data_sets = df_all['dataset'].unique()
				cache_sizes = df_all['cache_size'].unique()
				algorithms = df_all['algo'].unique()

				#print(algorithms)
				#print(data_sets)
				#print(cache_sizes)

				for trace_set in data_sets:
					curr_traces = df_all[df_all['dataset']==trace_set]

					out = str(trace_set) + ": {}".format(len(df_all[df_all['dataset']==trace_set]))
					pretty.success(out)
				pretty.success("Total_number_of_experiments: {}".format(len(df_all)))

				
				num_traces = len(df_all)

				sorted_df = df_all.sort_values(['dataset', 'cache_size', 'traces', 'hit_rate', 'rank'], 
				                               ascending=[True, True, True, False, True])

				dif = df_all.sort_values(['rank'], 
				                               ascending=[True])

				min_ids = sorted_df.groupby(['dataset', 'cache_size', 'traces'])['rank'].transform(min) == sorted_df['rank']
				sorted_min_df = sorted_df[min_ids]
				sorted_min_grouped = sorted_min_df.groupby(['dataset', 'cache_size'])


				algo_top_count = []

				for name, group in sorted_min_grouped:

					for algo in algorithms:
						alg_rows = group.loc[group['algo'] == algo]
						dataset = group.iloc[0]['dataset']
						cache_size = group.iloc[0]['cache_size']
						alg_count = len(alg_rows)
						algo_top_count.append([dataset, cache_size, algo, round(alg_count/len(group) * 100, 1)])


				for_heat_map = pd.DataFrame(algo_top_count)
				for_heat_map.columns = ['dataset', 'cache_size', 'algo', 'percentage']
				sorted_heat_map = for_heat_map.sort_values(['dataset', 'cache_size', 'algo'], ascending=[True, True, True])

				sorted_heat_map = for_heat_map.sort_values(['dataset', 'cache_size', 'algo'], ascending=[True, True, True])
				heatmap_data = pd.pivot_table(sorted_heat_map, values='percentage', 
				                     index=['algo'], 
				                     columns=['dataset', 'cache_size'])

				algorithms = sorted_heat_map['algo'].unique()

				print(heatmap_data)

				for things in algorithms:
					print(things)

				#we get rid of trailing zeroes and trailing periods that result from multiplying floats so that it will display as before when it was hardcoded
				# "0.05", "0.1", "0.5", "1", "5", "10"
				labels = []
				for vals in cache_sizes:
					vals = vals * 100
					labels.append(str(vals).rstrip('0').rstrip('.') )
				labels = labels * len(data_sets)

				
				#tick_l = [0.1, 0.3, 0.5, 0.7, 1.1]
				#tick_g = [0.1, 0.3, 0.5, 0.7, 0.9]

				# generate tick positions based on number of data sets used.I used '0.1' here to get output similar to what was hardcoded,
				# but in all likelihood an option to add an offset will be needed for different CSVs that have different dimensions.
				#
				# these tick position values correspond to where the labels on the top will be placed. 
				tick_position_data_set_label = []
				for trace_groups in range(len(data_sets)):
					position = 0.1 + (trace_groups * 1/len(data_sets))
					tick_position_data_set_label.append(position)

				#print(tick_position_data_set_label)



				#tick_y = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]


				#these correspond to where the algorithms labels on the left go
				tick_position_alg_label = []
				for number_of_algs in range(len(algorithms)):
					tick_position_alg_label.append(number_of_algs + .5)

				#tick_y = [10, 20, 30, 40, 50, 60]
				mid = (for_heat_map['percentage'].max() - for_heat_map['percentage'].min()) / 2

				print("--------------")


				fig, ax1 = plt.subplots(figsize=(13.2, 2.45))
				sb.set_style('white')
				ax1 = sb.heatmap(heatmap_data,cmap="Greens", annot=True, center=mid, cbar=False, annot_kws={"size": 13})

				ax2 = ax1.twiny()
				ax1.set_xticklabels(labels, fontsize=15)


				#test = ["ARC", "DLIRS", "LeCaR", "LFU", "LIRS", "LRU", "C1", "C2", "C3"]

				ax1.set_yticklabels(algorithms, fontsize=15)
				ax1.set_yticks(tick_position_alg_label)
				ax2.set_xticklabels(data_sets, fontsize=15)
				ax2.set_xticks(tick_position_data_set_label)

				ax1.set_xlabel("cache size(% of workload footprint)")
				ax1.set_ylabel("")
				fig.savefig('figure2.png', format='png', bbox_inches = 'tight', dpi=600)
				plt.show()

# this method contacts MongoDB for the data needed to generate the heatmap grid for each dataset, algorithm and cache size permutation.
# as of 8/4/2020 the generation of the heat map is still dependent on the actual experiment data to get the full set of datasets, algorithms
# and cache sizes. 
# The goal is to allow a user to choose datasets, algorithms and cache sizes from the ones stored to generate their own heat map data.
# so the line containing "datasets, algs, sizes = nr.get_unique_field_list()" should be replaced with arguments specifying a list of 
# datasets, algs and sizes specified by the user.

def amended_dash_rank_heat_map(custom_datasets, custom_algos, custom_sizes, req_id = None):

	#datasets, algorithms, sizes = nr.get_unique_field_list()
	datasets = custom_datasets
	algorithms = custom_algos
	sizes = custom_sizes
	
	print("amended called")
	#out = heat_map_find(['arc'], [0.001], ['FIU', 'CloudCache'])


	if req_id != None:
		conduit.current_status[req_id] = "retrieving hit rate data for heat map from mongo..."

	#m_heat_data = storage.heat_map_find(algorithms, sizes, datasets)

	m_heat_data = []

	for a in algorithms:
		for s in sizes:
			for d in datasets:
				res = storage2.find_in_collection_multi("alg_runs", [{"dataset":d}, {"cache_size":s}, {"algorithm": a}])

				m_heat_data.extend(res)

	inter_df = pd.DataFrame(m_heat_data)
	#values are sorted and ranked by hit rate here. 
	if req_id != None:
		conduit.current_status[req_id] = "processing rank data..."

	#print(m_heat_data, "********************************************************")

	sorted_df = inter_df.sort_values(['dataset', 'cache_size', 'trace name', 'final hit rate'], ascending=[True, True, True, False])

	sorted_df['rank'] = sorted_df.groupby(['dataset', 'cache_size', 
                                       'trace name'])['final hit rate'].rank(ascending=False, method='dense')

	#this reranking process is to make all values within 5% of the rank 1 value also have a rank of 1
	reranked = []
	top_dat = []
	grouped = sorted_df.groupby(['dataset', 'cache_size', 'trace name'])
	for name, group in grouped:
		top_hit = group.iloc[0]['final hit rate'].item()
		top_dat.append(top_hit)
		five_p_less = top_hit * 0.95
		for index, row in group.iterrows():
			#print(row)
			if row['final hit rate'] >= five_p_less:
				row['rank'] = 1
				reranked.append(row)
	df_all = pd.DataFrame(reranked)
	# print(reranked_df)
	'''df_all.columns = ['_id', 'trace name', 'algorithm', 'cache_size', 'date', 'final hit rate', 
    'final misses', 'final pollution', 'hit rate array uploaded to minio', 'ios', 
    'miss rate array uploaded to minio', 'pollution array uploaded to minio', 'total hits', 'dataset', 'rank']'''

	df_all.columns = ['_id', 'algorithm', 'cache_size', 'dataset', 'date', 'final hit rate',
    'final misses', 'final pollution', 'hit rate array uploaded to minio', 'ios', 
    'miss rate array uploaded to minio', 'pollution array uploaded to minio', 'total hits',  'trace name',  'rank']

	print("+++++++++++++++++++++++++++++++++")
	'''with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		print(df_all)'''
	
    #['_id', 'algorithm', 'cache_size', 'dataset', 'date', 'final hit rate', 
    #'final misses', 'final pollution', 'hit rate array uploaded to minio', 'ios', 
    #'miss rate array uploaded to minio', 'pollution array uploaded to minio', 'total hits', 'trace name']

	data_sets = df_all['dataset'].unique()
	cache_sizes = df_all['cache_size'].unique()
	algorithms = df_all['algorithm'].unique()


	print(data_sets, "DATA SETS")
	print(cache_sizes, "CACHE SIZES")
	print(algorithms, "ALGORITHMS")

	#this is getting data necessary to plot on the Dash web app

	x_cache_sizes = [] # cache_sizes.tolist() * len(data_sets)
	for ds in data_sets:
		for x in cache_sizes:
			x_cache_sizes.append(str(x) + " " + str(ds)) #1st 8 letters of dataset name
	y_algorithms = algorithms.tolist()
	y_algorithms.sort()


	
	for trace_set in data_sets:
		curr_traces = df_all[df_all['dataset']==trace_set]

		out = str(trace_set) + ": {}".format(len(df_all[df_all['dataset']==trace_set]))
		pretty.success(out)
	pretty.success("Total_number_of_experiments: {}".format(len(df_all)))

	#sort all the data and then group then group by rank	
	num_traces = len(df_all)

	sorted_df = df_all.sort_values(['dataset', 'cache_size', 'trace name', 'final hit rate', 'rank'], 
				                            ascending=[True, True, True, False, True])

	dif = df_all.sort_values(['rank'], ascending=[True])

	min_ids = sorted_df.groupby(['dataset', 'cache_size', 'trace name'])['rank'].transform(min) == sorted_df['rank']
	sorted_min_df = sorted_df[min_ids]
	sorted_min_grouped = sorted_min_df.groupby(['dataset', 'cache_size'])


	algo_top_count = []
	#take only the #1 ranked values			
	for name, group in sorted_min_grouped:

		for algo in algorithms:
			alg_rows = group.loc[group['algorithm'] == algo]
			dataset = group.iloc[0]['dataset']
			cache_size = group.iloc[0]['cache_size']
			alg_count = len(alg_rows)
						
			algo_top_count.append([dataset, cache_size, algo, round(alg_count/len(group) * 100, 1)])

	#create a dataframe of resulting data.
	for_heat_map = pd.DataFrame(algo_top_count)
	for_heat_map.columns = ['dataset', 'cache_size', 'algorithm', 'percentage']
	#sorted_heat_map = for_heat_map.sort_values(['dataset', 'cache_size', 'algo'], ascending=[True, True, True])

	sorted_heat_map = for_heat_map.sort_values(['dataset', 'algorithm', 'cache_size'], ascending=[True, True, True])
				
	heatmap_data = pd.pivot_table(sorted_heat_map, values='percentage', 
				                  index=['algorithm'], 
				                  columns=['dataset', 'cache_size'])
				
	print(x_cache_sizes)
	print('======================')
	print(y_algorithms)
	print('======================')
	data = heatmap_data.to_numpy()
	#print(data)
	
	
	return x_cache_sizes, y_algorithms, data




				
