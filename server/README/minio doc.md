# Minio Module readme:

The keys that are used for the items in the Minio Module are the item keys for that trace in MongoDB.
For example if you have a trace named example-trace.blkparse and its ID in Mongo is 1234567e 
All of the corresponding data in minio is labelled as 1234567e with a flag for whatever data it is.
1234567e-H for hit rate and so on.

====================================================


====================================================

### insert(file, id):

input: 

	file (string of filepath for document to insert), id(string with what ID you want to give the object)
output: 

	False if there is an error, True if upload succeeded

====================================================

====================================================
### retrieve(file, id):

input: 

	file (string of filepath for file to be saved as), id(string with what ID you want to retrieve from minio)

output: 

	False if file was not found, True if file was found

====================================================
### download_to_mem(iden):

#### this function was supposed to hold the contents of the compressed NPZ in memory to avoid downloading the file to disk and unzipping from there.
#### however, since the data is stored in binary mode, decoding the compressed file became an issue. As such, this function is not used, however it works.

input: 

	iden(id of desired minio object)

output: 

	bytebuffer of the minio object data

===================================================

### delete_all():

deletes everything in the minio store

===================================================

===================================================
### delete_item(del_key):


input: 

	del_key(string that corresponds to the ID of object you want to delete)

output: 

	False if there is a client error, else True

==================================================

===================================================

==================================================


===================================================
### exist(ident):


input:

	ident(minio object ID)

output: 

	True if object exists, else False

==================================================
