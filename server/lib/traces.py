from .optional_args import process_kwargs


# Basic Trace Reader as Base Class
class Trace:
    def __init__(self, file, **kwargs):
        # Duration (in Hours)
        self.duration = 0

        process_kwargs(self, kwargs, acceptable_kws=['duration'])

        # Setup
        self.file = file
        self.unique = set()
        self.reuse = set()
        self.writes = []
        self.requests = 0
        self.start_time = 0

        # Progress (0-100%)
        self.progress = 0

        # get ending index of file for progress
        f = open(self.file, 'r')
        f.seek(0, 2)
        #self.end = f.tell()
        f.close()

    def readLine(self, line):
        yield int(line), False

    def read(self):
        f = open(self.file, 'r')
        try:
            while True:
                line = f.readline()
                if not line: break
                # self.progress = round(100 * (f.tell() / self.end))
                for lba, write in self.readLine(line):
                    if lba == None: continue
                    self.requests +=1

                    if lba in self.unique:
                        self.reuse.add(lba)
                    self.unique.add(lba)

                    yield lba, write
        except EOFError:
            pass
        f.close()

    def num_requests(self):
        return self.requests

    def num_unique(self):
        return len(self.unique)

    def num_reuse(self):
        return len(self.reuse)
    
    def num_writes(self):
        return len(self.writes)

class FIUTrace(Trace):
    def inDuration(self, time):
        if self.duration == 0:
            return True

        if self.start_time == 0:
            self.start_time = time
            self.end_time = time + (self.duration * 10**9 * 60 * 60)

        return time < self.end_time

    def readLine(self, line):
        blocks_per_page = 8
        line = line.split(' ')

        ts = int(line[0])
        lba = int(line[3])
        size = int(line[4])
        write = line[5][0] == 'W'
        align = lba % blocks_per_page
        lba -= align
        size += align
        
        if write:
            self.writes.append(lba)

        if not self.inDuration(ts):
            raise EOFError("End of duration")

        for offset in range(0, size, blocks_per_page):
            yield lba + offset, write


class MSRTrace(Trace):
    def inDuration(self, time):
        if self.duration == 0:
            return True

        if self.start_time == 0:
            self.start_time = time
            self.end_time = time + (self.duration * 10**7 * 60 * 60)

        return time < self.end_time

    def readLine(self, line):
        blocksize = 512
        line = line.split(',')

        ts = int(line[0])
        write = line[3][0] == 'W'
        lba = int(line[4])
        size = int(line[5])
        align = lba % blocksize
        lba -= align
        size += align

        if not self.inDuration(ts):
            raise EOFError("End of duration")
        
        if write: 
            self.writes.append(lba)

        for offset in range(0, size, blocksize):
            yield lba + offset, write


class VisaTrace(Trace):
    def readLine(self, line):
        blocks_per_page = 8
        line = line.split(' ')
        lba = int(line[4])
        size = int(line[5])
        write = line[6][0] == 'W'
        align = lba % blocks_per_page
        lba -= align
        size += align

        if write: 
            self.writes.append(lba)   

        for offset in range(0, size, blocks_per_page):
            yield lba + offset, write


class NexusTrace(Trace):
    def readLine(self, line):
        blocks_per_page = 8
        line = line.split("\t\t")
        lba = int(line[0])
        size = int(line[1])
        write = int(line[3]) == 3 or int(line[3]) == 5

        if write: 
            self.writes.append(lba)

        for offset in range(0, size, blocks_per_page):
            yield lba + offset, write


class UMassTrace(Trace):
    def readLine(self, line):
        blocksize = 512
        line = line.split(',')
        lba = int(line[1])
        size = int(line[2])

        if write: 
            self.writes.append(lba)

        for offset in range(0, size, blocksize):
            yield lba + offset, False


class SynthTrace(Trace):
    def readLine(self, line):
        lba = int(line)
        if lba < 0:
            yield None, False
        else:
            yield lba, False


def get_trace_reader(trace_type):
    trace_type = trace_type.lower()
    if trace_type == 'fiu':
        return FIUTrace
    if trace_type == 'msr':
        return MSRTrace
    if trace_type == 'visa':
        return VisaTrace
    if trace_type == 'nexus':
        return NexusTrace
    if trace_type == 'umass':
        return UMassTrace
    if trace_type == 'synth':
        return SynthTrace
    raise ValueError("Could not find trace reader for {}".format(trace_type))


def identify_trace(filename):
    if filename.endswith('.blkparse'):
        return 'fiu'
    if filename.endswith('.csv'):
        return 'msr'
    if filename.endswith('.blk'):
        return 'visa'
    if filename.endswith('.txt'):
        return 'nexus'
    if filename.endswith('.spc'):
        return 'umass'
    if filename.endswith('.trc') or filename.endswith('.tx'):
        return 'synth'
    raise ValueError("Could not identify trace type of {}".format(filename))


def read_trace_file(filename):
    trace_type = identify_trace(filename)
    trace_reader = get_trace_reader(trace_type)
    reader = trace_reader(filename)
    for lba, write in reader.read():
        yield lba, write


if __name__ == '__main__':
    import sys
    for lba, write in read_trace_file(sys.argv[1]):
        print(lba, write)
