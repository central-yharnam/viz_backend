import pysftp as sftp
import io
#import sf_filereader
import csv
import json
import os

hostname = os.environ['SF_SERVER']
username = os.environ['SF_USERNAME']
password = os.environ['SF_PASSWORD']

with open(os.environ['SF_SERVER']) as f:
    entry = f.read()
hostname = entry

with open(os.environ['SF_USERNAME']) as f:
    entry = f.read()
username = entry

with open(os.environ['SF_PASSWORD']) as f:
    entry = f.read()
password = entry

def list_sftpshared_traces(trace):
    cnopts = sftp.CnOpts()
    cnopts.hostkeys = None
    con = sftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts)
    print("connected")

    # Switch to a remote directory
    con.cwd('/home/cache-research/')


    file_names = []
    dir_names = []
    un_name = []
    read_var = io.BytesIO()
    #read_var = io.StringIO()
    def store_files_name(fname):

        file_names.append(fname) 

    def store_dir_name(dirname):

        dir_names.append(dirname)

    def store_other_file_types(name):

        un_name.append(name)

    con.walktree("/home/cache-research/",store_files_name,store_dir_name,store_other_file_types,recurse=True)

    file = open('paths.txt', 'w')
    file.write(str(file_names))

    #print(file_names, "files")
    #print(dir_names, "directories")
    #print(un_name, "dont know")

    read_var.seek(0)
    #print(read_var.readline())
    #print(type(read_var.readline()))

    wrapper = io.TextIOWrapper(read_var, encoding='utf-8')
    #print(wrapper)

    #dlt = "," if (trace.endswith('.csv')) else " "

    # trace_obj, delim = identify_trace(trace_path)
    #csv_trace = csv.reader(wrapper, delimiter=dlt)
    
    '''reader = sf_filereader.identify_trace(trace, wrapper)
    for lba in reader.read_all():
    	print(lba)'''

def sftp_get_trace(trace):
    cnopts = sftp.CnOpts()
    cnopts.hostkeys = None
    con = sftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts)
    print("connected")

    # Switch to a remote directory
    con.cwd('/home/cache-research/')


    file_names = []
    dir_names = []
    un_name = []
    read_var = io.BytesIO()
    filename = []
    #read_var = io.StringIO()
    def store_files_name(fname):

        if trace in fname:
            print(fname)
            print(trace)
            print(type(fname))
            #con.getfo(fname, read_var)
            print("gotten")
            path = fname.split('/')
            filename.append(path[-1])
            #print(path)
            #print(filename)
            #return filename
        pass
        #file_names.append(fname) 

    def store_dir_name(dirname):
    	pass
        #dir_names.append(dirname)

    def store_other_file_types(name):
    	pass
        #un_name.append(name)

    con.walktree("/home/cache-research/",store_files_name,store_dir_name,store_other_file_types,recurse=True)


    read_var.seek(0)


    wrapper = io.TextIOWrapper(read_var, encoding='utf-8')
    return filename[0], wrapper





#list_sftpshared_traces('web_0.csv')

def path_list():
	a = open('paths.txt', 'r')
	#res = json.loads(ini_list) 
	print(a)
	for it in a:
		#print(type(it))
		#print(it)

		paths = it.strip('][').split(', ') 
		#print(it)
		#print(type(paths))
	#print(type(paths))

	'''for a in paths:
		print(a, type(a))'''
	return paths

def direct_query(trace):
    print("in direct query")
    cnopts = sftp.CnOpts()
    cnopts.hostkeys = None
    con = sftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts)
    print("connected")

    # Switch to a remote directory
    con.cwd('/home/cache-research/')


    file_names = []
    dir_names = []
    un_name = []
    read_var = io.BytesIO()
    filename = None
    #read_var = io.StringIO()

    paths = path_list()
    count = 0
    #the file name has an extra ' symbol that throws off the get function so it has to be replaced with an empty string
    for files in paths:
    	if trace in files and "small" not in files and count == 0:
    		print(files)
    		con.getfo(files.replace("\'", ""), read_var)
    		path = files.split('/')
    		filename = path[-1].replace("\'", "")
    		print(filename)
    		count += 1
    read_var.seek(0)


    wrapper = io.TextIOWrapper(read_var, encoding='utf-8')
    print(wrapper)
    return filename, wrapper


#direct_query('webusers-030409-033109.13.blkparse')
#sftp_get_trace("webusers-030409-033109.13.blkparse")
#path_list()