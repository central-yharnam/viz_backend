Minio Module:

The keys that are used for the items in the Minio Module are the item keys for that trace in MongoDB.
For example if you have a trace named example-trace.blkparse and its ID in Mongo is 1234567e 
All of the corresponding data in minio is labelled as 1234567e with a flag for whatever data it is.
1234567e-H for hit rate and so on.

insert(file, id): arguments are filepath (string) and ID (string). the file at filepath is uploaded to Minio and is stored as 
		  what was passed as ID.

retrieve(file, id): find file with given ID and write it to filepath specified.

delete_item(del_key): specify the key of the item you want to delete. 

exist(ident): check if an item exists in that database. 