# storage2 readme:

#### the methods in storage all contact MongoDB
#### contact to MongoDB is done through the pymongo interface

=======================================================
### find_in_collection(collection_name, param=None): 
input: 

	collection name (string), 
	param (an array where the first value is a string with the field to search in, and the second
	value is a string with the value to find)

output: 

	list of items with that value in field. if param is not given, all items in collection are returned. 


=======================================================

=======================================================
### insert_to_collection(collection_name, data): 

specify a collection in the database to insert JSON file to

input: 

	collection name (string)
	data (JSON formatted string)

output:

	id of inserted value, returns false if there was an error with the transaction

=======================================================

=======================================================
### delete_one_from_collection(collection_name, field, value): 

specify collection in the database to delete one item from

input: 

	collection name (string)
	field (string)
	value (string)

output:


	returns DeleteResult instance

=======================================================

=======================================================
### delete_many_from_collection(collection_name, field, value): 

specify collection in the database to delete all items with field and value

input: 

	collection name (string)
	field (string)
	value (string)

output:


	returns DeleteResult instance

=======================================================
=======================================================
### find_distinct_fields(collection_name, field): 

specify collection and field, find all distinct values in that field.

input:

	collection_name (string)
	field (string)

output:

	list of distinct values

	

=======================================================
=======================================================
### insert_many(collection_name, data_list):

uses bulk insert for inserting many items. if you are importing a large amount of data this is what should be used.

input:

	collection_name (string)
	data_list (list of all JSON entries to insert into database)

output:


	returns data on all the entries uploaded

=======================================================
