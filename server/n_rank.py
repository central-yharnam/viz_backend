import pandas as pd

def p_csv():
	df_all = pd.read_csv('./clean_final_results_all.csv', header=None)
	df_all.columns = ['traces', 'trace_name', 'algo', 'hits', 'misses', 'writes', 'filters', 
	                   'size', 'cache_size', 'requestcount', 'hit_rate', 'time', 'dataset']

	#df_dum = df_all.iloc[0:50]
	#print(df_dum)

	#dictio = df_dum.to_dict('records')
	dictio = df_all.to_dict('records')
	'''for item in dictio:
		print(item)'''
	#print(len(dictio))
	'''dataset = df_all['dataset'].unique()
	#print(dataset)
	algo = df_all['algo'].unique()
	#print(algo)
	cs = df_all['cache_size'].unique()
	#print(cs)
	for items in cs:
		print(items, type(items))'''

	'''for ds in dataset:
		print(len(df_all[df_all['dataset'] == ds]) )'''
	#print(type(dictio))

	'''for ds in dataset:
		df_cur_ds = df_all[df_all['dataset'] == ds]
		current_dictionary = df_cur_ds.to_dict('records')'''
	#print(dictio)
	return dictio

def get_unique_field_list():
	df_all = pd.read_csv('./clean_final_results_all.csv', header=None)
	df_all.columns = ['traces', 'trace_name', 'algo', 'hits', 'misses', 'writes', 'filters', 
	                   'size', 'cache_size', 'requestcount', 'hit_rate', 'time', 'dataset', 'extra']

	#dictio = df_dum.to_dict('records')
	dictio = df_all.to_dict('records')
	'''for item in dictio:
		print(item)'''
	#print(len(dictio))
	dataset = df_all['dataset'].unique()
	#print(dataset)
	algo = df_all['algo'].unique()
	#print(algo)
	cs = df_all['cache_size'].unique()
	#print(cs)

	'''for ds in dataset:
		print(len(df_all[df_all['dataset'] == ds]) )'''
	#print(type(dictio))

	'''for ds in dataset:
		df_cur_ds = df_all[df_all['dataset'] == ds]
		current_dictionary = df_cur_ds.to_dict('records')'''
	#print(dictio)
	return dataset, algo, cs

#p_csv()