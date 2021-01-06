from storage import *
import pandas as pd
import n_rank as nr

datasets, algs, sizes = nr.get_unique_field_list()

#out = heat_map_find(['arc'], [0.001], ['FIU', 'CloudCache'])
out = heat_map_find(algs, sizes, datasets)
print(len(out))

df = pd.DataFrame(out)
print(df)
print(list(df.columns)) 