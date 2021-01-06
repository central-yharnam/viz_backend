from .lib.traces import identify_trace, get_trace_reader
from .lib.progress_bar import ProgressBar
from .algs.get_algorithm import get_algorithm
from timeit import timeit
from itertools import product
import numpy as np
import csv
import os

progress_bar_size = 30


class AlgorithmTest:
    def __init__(self, algorithm, cache_size, trace_file, alg_args, **kwargs):
        self.algorithm = algorithm
        self.cache_size = cache_size
        self.trace_file = trace_file
        self.alg_args = alg_args

        trace_type = identify_trace(trace_file)
        trace_reader = get_trace_reader(trace_type)
        self.reader = trace_reader(trace_file, **kwargs)

        self.misses = 0

    def _run(self):
        alg = get_algorithm(self.algorithm)(self.cache_size, **self.alg_args)
        progress_bar = ProgressBar(progress_bar_size,
                                   title="{} {}".format(
                                       self.algorithm, self.cache_size))
        for lba in self.reader.read():
            if alg.request(lba):
                self.misses += 1
            progress_bar.progress = self.reader.progress
            progress_bar.print()
        progress_bar.print_complete()
        self.avg_pollution = np.mean(alg.pollution.Y)

    def run(self, config):
        time = round(timeit(self._run, number=1), 2)
        ios = self.reader.num_requests()
        hits = ios - self.misses
        print(
            "Results: {:<10} size={:<8} hits={}, misses={}, hitrate={:4}% avg_pollution={:4}% {:8}s {}"
            .format(self.algorithm, self.cache_size, hits, self.misses,
                    round(100 * hits / ios, 2), round(self.avg_pollution, 2),
                    time, self.trace_file, *self.alg_args.items()))

        if "output_csv" in config:
            self.writeCSV(config["output_csv"], hits, ios, time)

    def writeCSV(self, filename, hits, ios, time):
        with open(filename, 'a+') as csvfile:
            writer = csv.writer(csvfile,
                                delimiter=',',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                self.trace_file, self.algorithm, hits, self.misses,
                self.cache_size,
                round(100 * hits / ios, 2),
                round(self.avg_pollution, 2), time, *self.alg_args.items()
            ])


def getUniqueCount(trace_name, kwargs):
    trace_type = identify_trace(trace_name)
    trace_reader = get_trace_reader(trace_type)
    reader = trace_reader(trace_name, **kwargs)

    progress_bar = ProgressBar(progress_bar_size, title="Counting Uniq")

    for lba in reader.read():
        progress_bar.progress = reader.progress
        progress_bar.print()
    progress_bar.print_complete()

    return reader.num_unique()


def generateTraceNames(trace):
    if trace.startswith('~'):
        trace = os.path.expanduser(trace)

    if os.path.isdir(trace):
        for trace_name in os.listdir(trace):
            yield os.path.join(trace, trace_name)
    elif os.path.isfile(trace):
        yield trace
    else:
        raise ValueError("{} is not a directory or a file".format(trace))


def generateAlgorithmTests(algorithm, cache_size, trace_name, config):
    alg_config = {}
    if algorithm in config:
        keywords = list(config[algorithm])
        for values in product(*config[algorithm].values()):
            for key, value in zip(keywords, values):
                alg_config[key] = value
            yield AlgorithmTest(algorithm, cache_size, trace_name, alg_config,
                                **config)
    else:
        yield AlgorithmTest(algorithm, cache_size, trace_name, alg_config,
                            **config)


if __name__ == '__main__':
    import sys
    import json
    import math
    import os

    with open(sys.argv[1], 'r') as f:
        config = json.loads(f.read())

    for trace in config['traces']:
        for trace_name in generateTraceNames(trace):
            if any(map(lambda x: x < 1.0, config['cache_sizes'])):
                unique = getUniqueCount(trace_name, config)

            for cache_size in config['cache_sizes']:
                tmp_cache_size = cache_size
                if cache_size < 1.0:
                    cache_size = math.floor(cache_size * unique)
                if cache_size < 10:
                    print(
                        "Cache size {} too small for trace {}. Calculated size is {}. Skipping"
                        .format(tmp_cache_size, trace_name, cache_size),
                        file=sys.stderr)
                    continue

                for algorithm in config['algorithms']:
                    for test in generateAlgorithmTests(algorithm, cache_size,
                                                       trace_name, config):
                        test.run(config)
