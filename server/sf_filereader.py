import csv
import time

#the only difference is that the genreader doesnt open a path

class GenReader:
    # generic class
    def __init__(self, trace_path, trace_data):
        self.requests = 0
        self.writes = 0
        self.uniques = 0 
        self.reuses = 0
        self.all_blocks = {} # can be used instead of current request frequency...?
        self.path = trace_path
        self.time_stamp = []
        self.data = trace_data
    #   generic reader 
    #   for any line in any file
    #   individual lines read by function of trace's specific class
    # ==========================
    def read_all(self):
        #file = open(self.path) 

        # might need a more complicated branch for delimiters
        dlt = "," if (self.path.endswith('.csv')) else " "

        # trace_obj, delim = identify_trace(trace_path)
        csv_trace = csv.reader(self.data, delimiter=dlt)


        for row in csv_trace:
            for lba, write, current_time in self.read_line(row):
                self.requests += 1
                self.writes += write
                if current_time is None: current_time = self.requests
                self.time_stamp.append(current_time)
                try:
                    seen = self.all_blocks[lba]
                    if seen == 1:
                        self.all_blocks[lba] += 1
                        self.reuses += 1
                except:
                    self.all_blocks[lba] = 1
                    self.uniques += 1
                yield lba, write
        #file.close() 


# ===== MSR reader =====
class MSRReader(GenReader):
    
    def read_line(self, row):
        blocksize = 512 # ---- from MSR, block size  
        current_time = int(row[0])
        lba = int(row[4])
        size = int(row[5])
        align = lba % blocksize
        lba -= align
        size += align
        wr = 1 if (row[3][0] == 'W') else 0
        if size % blocksize > 0:
            size += blocksize
        
        for offset in range(0, size, blocksize):
            yield (lba + offset), wr, current_time


# ==== FIU reader ====
class FIUReader(GenReader):

    def read_line(self, row):
        blocks_per_page = 8
        wr = 1 if (row[5][0] == 'W') else 0
        current_time = int(row[0])
        lba = int(row[3])
        size = int(row[4])
        align = lba % blocks_per_page
        lba -= align
        size += align
        if size % blocks_per_page > 0:
            size += blocks_per_page

        for offset in range(0, size, blocks_per_page):
            yield (lba + offset), wr, current_time



class VisaReader(GenReader):
    
    def read_line(self, row):
        blocks_per_page = 8
        #line = row.split(' ')
        line = row
        lba = int(line[4])
        size = int(line[5])
        wr = 1 if (line[6][0] == 'W') else 0  

        for offset in range(0, size, blocks_per_page):
            # self.requests stands in for time
            yield (lba + offset), wr, None


class NexusReader(GenReader):
    def read_line(self, row):
        pass


class UmassReader(GenReader):
    def read_line(self, row):
        blocksize = 512
        line = row.split(',')
        lba = int(line[1])
        size = int(line[2])

        for offset in range(0, size, blocksize):
            # self.requests stands in for time
            yield (lba + offset), False, None


class SynthReader(GenReader):
    def read_line(self, row):
        lba = int(row)
        if lba < 0:
            yield None, False
        else:
            # self.requests stands in for time
            yield lba, False, None

# ==========================
# identify trace type based on filename extension
# create a Reader object based on trace type
# ==========================
def identify_trace(file, data):
    if file.endswith('.csv'):
        return MSRReader(file, data)
    if file.endswith('.blkparse'):
        return FIUReader(file, data)
    if file.endswith('.blk'):
        return VisaReader(file, data)
    if file.endswith('.txt'):
        return NexusReader(file, data)
    if file.endswith('.spc'):
        return UmassReader(file, data)
    if file.endswith('.trc') or file.endswith('.tx'):
        return SynthReader(file, data)
    raise ValueError("Could not identify trace type of {}".format(file))

# copy of MSRtrace class in visualize/VisualCache/lib/traces.py
# version 1 of reader with csv alone 
def msr_trace_csv(trace_path):
    file = open(trace_path)
    csv_trace = csv.reader(file)

    requests, writes, uniques, reuses = 0, 0, 0, 0
    all_blocks = {}

    blocksize = 512 # ---- from MSR, block size
    for row in csv_trace:

        lba = int(row[4])
        size = int(row[5])
        align = lba % blocksize
        lba -= align
        size += align
        if size % blocksize > 0:
            size += blocksize
        
        if row[3][0] == 'W': writes += 1 

        for offset in range(0, size, blocksize):
            
            requests += 1
            item = lba + offset
            # count uniques and repeats
            try:
                seen = all_blocks[item]
                if seen == 1:
                    all_blocks[item] += 1
                    reuses += 1
            except:
                all_blocks[item] = 1
                uniques += 1
    file.close() 
    return requests, writes, uniques, reuses
     
# --------------------------
if __name__ == '__main__':
    t1 = time.perf_counter()
    trace_name = "C:/Users/cyan/python_projects/CAM-02-SRV-lvm0.csv"

    t_reader = identify_trace(trace_name)

    for lba in t_reader.read_all():
        pass
    t2 = time.perf_counter()
    print("requests: " + str(t_reader.requests))
    print("uniques: " + str(t_reader.uniques))
    print("reuses: " + str(t_reader.reuses))
    print("writes: " + str(t_reader.writes))

    print(f"-----------New CSV reader {(t2 - t1):0.8f} s.")
