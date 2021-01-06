from lib.traces import identify_trace, get_trace_reader
from lib.progress_bar import ProgressBar
from algs.get_algorithm import get_algorithm
from timeit import timeit
from itertools import product
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import json
import visual.StatVis as sv
from StatGen import *
import visual_utils as vu
import server_utils as serv
import pandas as pd
import csv_plot
import pretty

#import storage as stor


cwd = os.getcwd()
save_path = cwd + '/output/'

progress_bar_size = 30


def is_valid_file(parser, arg):
    """
    Check if arg is a valid file that already exists on the file system.
    """
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def get_parser():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--file",
                        dest="filename",
                        type=lambda x: is_valid_file(parser, x),
                        help="This is not working for now such a placeholder",
                        metavar="FILE")
    parser.add_argument("-s", "--stats",
                        dest="stat", 
                        default=False,
                        help="Generate the statistics for a trace", 
                        action="store_true")
    parser.add_argument("-p", "--access-pattern",
                        dest="pattern",
                        default=False,
                        help="Generate the trace access pattern",
                        action="store_true")
    parser.add_argument("-H", "--hit-ratevstime",
                        dest="hrt",
                        default=False,
                        help="Generate the Hit Rate vs time for the algorithms specified in the config file", 
                        action="store_true")
    parser.add_argument("-q", "--quiet",
                        action="store_false",
                        dest="verbose",
                        default= False,
                        help="This is not working just a template to be implemented later")
    parser.add_argument("-a", "--algstats",
                        dest="algstat", 
                        default=False,
                        help="Generate the algorithm statistics for traces in the config file", 
                        action="store_true")
    parser.add_argument("-P", "--pollution",
                        dest="polgraph",
                        default = False,
                        help="Graphs the pollution of cache using specified algorithms over time. It is necessary to run -s and -as before using this command",
                        action ="store_true")

    parser.add_argument("-g", "--histogram",
                        dest="histo",
                        default = False,
                        help="Generates a bar graph of how many times each LBA is called",
                        action ="store_true")

    parser.add_argument("-m", "--miss rate curve",
                        dest="miss",
                        default = False,
                        help="Generates a graph for the miss rate curve",
                        action ="store_true")

    parser.add_argument("-d", "--dlirs HIR stack",
                        dest="dlirs_stack",
                        default = False,
                        help="Generates a graph of the size of the dlirs HIR stack over time",
                        action ="store_true")

    parser.add_argument("-l", "--lecar lru over time",
                        dest="lecar_lru",
                        default = False,
                        help="Generates a graph of the lecar lru value over time",
                        action ="store_true")

    parser.add_argument("-w", "--arc p value over time",
                        dest="arc_p",
                        default = False,
                        help="Generates a graph of the arc p value over time",
                        action ="store_true")

    parser.add_argument("-x", "--cacheus learning rate over time",
                        dest="cacheus_learning_rate",
                        default = False,
                        help="Generates a graph of the cacheus learning rate value over time",
                        action ="store_true")

    parser.add_argument("-y", "--cacheus lru over time",
                        dest="cacheus_lru",
                        default = False,
                        help="Generates a graph of the cacheus lru value over time",
                        action ="store_true")

    parser.add_argument("-z", "--cacheus q over time",
                        dest="cacheus_q",
                        default = False,
                        help="Generates a graph of the cacheus lru value over time",
                        action ="store_true")

    parser.add_argument("-r", "--reuse distance for lba",
                        dest="reuse",
                        default = False,
                        help="Generates a graph of reuse distances",
                        action ="store_true")


    parser.add_argument("-t", "--test",
                        dest="test",
                        default = False,
                        help="testing",
                        action ="store_true")

    parser.add_argument("-c", "--csv heat map",
                        dest="csv_heat",
                        default = False,
                        help="generate heatmap from csv documents based on rank",
                        action ="store_true")

    parser.add_argument("-v", "--color fill hitrate comparison",
                        dest="versus",
                        default = False,
                        help="generate all pairs between algorithms specified in config and compare hitrates between the two for each cache size and trace",
                        action ="store_true")
    '''parser.add_argument("-R", "--real time request plotting",
                        dest="real_time",
                        default = False,
                        help="Plots requests in real time",
                        action ="store_true")'''

    return parser 




def test():
    print(os.path.exists('./b.txt'))

def compress_config(file):
    print("in compress config")
    name = "test"
    np.savez_compressed(name, file)

if __name__ == '__main__':
    import sys
    import math
    import json
    import os

    par = get_parser()
    args, unknown = get_parser().parse_known_args()
    if len(sys.argv) == 1:
        pretty.failure("no arguments passed")
        par.print_help()
        sys.exit()

    #check if the filepath passed as an argument is a valid filepath
    if (os.path.exists(sys.argv[1])):
        print(os.path.basename(sys.argv[1]))
        with open(sys.argv[1], 'r') as f:
            config = json.loads(f.read())

            name = os.path.basename(sys.argv[1])

            #storage.get_all_configs()
            
            #storage.remove_all_configs()

            '''if os.path.exists(config['output_path']) == False:
                os.mkdir(config['output_path'])
                print("config acquired")
                storage.insert_config(config, name)'''


            
    else: 
        pretty.failure("Error: config file {} does not exist".format(sys.argv[1]))
        sys.exit()

    args, unknown = get_parser().parse_known_args()


    # generate trace statistics. this is set to true by default because the number of unique accesses is needed to determine cache size 
    # for running -a flag later


    if args.test:
        pretty.utility("you have called test flag")
        #serv.check_config(config)
        #with open("reranked_5%_clean_final_results_all.csv", 'r') as file:

        #compress_config("reranked_5%_clean_final_results_all.csv")
        #b = np.load('test.npz')
        #print(b['arr_0'])

        #df = pd.read_csv('./reranked.csv')

        #compression_opts = dict(method='zip', archive_name='./reranked.csv')  
        #compression_opts = {'method': 'zip', 'archive_name': './reranked.csv'}

        #df.to_csv('out.zip', index=False, compression='zip')  

        #csv_plot.plot_rank_heat_map(config)
        #flag = "-H"
        #vu.visualize_head_to_head(config, flag, y_scale = None)

    if args.versus:
        flag = "-H"
        vu.visualize_head_to_head(config, flag, y_scale = None)

    if args.csv_heat:

        if config.get('rank') != None:
            serv.mongo_new_rank_csv(config)
            serv.minio_rank_csv_insert(config)
            csv_plot.plot_rank_heat_map(config)
        else:
            pretty.failure("No rank data specified in config for use of -c flag")
        #serv.check_config(config)
        #with open("reranked_5%_clean_final_results_all.csv", 'r') as file:

        #compress_config("reranked_5%_clean_final_results_all.csv")
        #b = np.load('test.npz')
        #print(b['arr_0'])

        #df = pd.read_csv('./reranked.csv')

        #compression_opts = dict(method='zip', archive_name='./reranked.csv')  
        #compression_opts = {'method': 'zip', 'archive_name': './reranked.csv'}

        #df.to_csv('out.zip', index=False, compression='zip')  

        

    if args.stat:


        #new online method, check for new traces in the mongo database
        newTraces = serv.mongo_new_paths(config)

        #iterate through list of new traces and upload them to minio
        if len(newTraces) > 0:
            for traces in newTraces:
                #print("uploading ", traces, " to mongodb")
                mongo_trace_id = singleTraceGen(traces)
                '''serv.s_minio_confirm(mongo_trace_id, traces)
                print("====================")
                serv.printMongoResults(traces)
                print("====================")'''

        #printTraceStats(config, configFileName)

    #generate access pattern for traces in config
    if args.pattern:

        #visualize_data('-p', config, 0)
        vu.visualize_data('-p', config)
                
    if args.reuse: 

        #reuse distance uses 2 different arrays
        #must pass 1 because the check will fail with 0
        vu.visualize_data('-r', config)


    #generate data for each trace for each algorithm and cache size
    if args.algstat:

        serv.mongo_new_alg_runs(config)
    
    
    #generate graph for frequency distribution of accesses
    if args.histo:

        vu.visualize_data('-g', config)

    #generate cache pollution graph over time
    #time is defined by the number of LBA requests being made. If there are 1000 lba requests that means 1000 units of time passed.
    if args.polgraph:

        #visualize_data('-P', config, 0)
        vu.visualize_data('-P', config)


    #generate hit rate over time plot 
    if args.hrt:
        print("HIT RATE CALLED")
        vu.visualize_data('-H', config, y_scale=100)
        #vu.visualize_data_multi('-H', config, y_scale=100)
        
    #generate miss rate curve over time
    if args.miss:

        vu.visualize_data('-m', config)


    # this is a simple utility that checks if the the algorithm data being requested for plotting is in the config file or not.
    # only relevant for the alg specific graphs such as cacheus learning rate
    def alg_check(config, algorithm):
        alg_present = 0
        for algorithms in config['algorithms']:
            if algorithms.lower() == algorithm.lower():
                alg_present = 1

        return alg_present 

    if args.dlirs_stack:

        #mongo_get_alg_run_plot_data(config, '-dlirs_stack')
        if alg_check(config, 'dlirs'):
            vu.visualize_data('-d', config)
        else:
            pretty.failure("dlirs algorithm not specified in config, this plotting flag -d is for visualizing dlirs data")



    if args.lecar_lru:

        if alg_check(config, 'lecar'):
            vu.visualize_data('-l', config)
        else:
            pretty.failure("lecar algorithm not specified in config, this plotting flag -l is for visualizing lecar data")

    if args.arc_p:
        if alg_check(config, 'arc'):
            vu.visualize_data('-w', config)
        else:
            pretty.failure("arc algorithm not specified in config, this plotting flag -w is for visualizing arc data")

    if args.cacheus_learning_rate:
        if alg_check(config, 'cacheus'):
            vu.visualize_data('-x', config)
        else:
            pretty.failure("cacheus algorithm not specified in config, this plotting flag -x is for visualizing cacheus data")

    if args.cacheus_lru:

        if alg_check(config, 'cacheus'):
            vu.visualize_data('-y', config)
        else:
            pretty.failure("cacheus algorithm not specified in config, this plotting flag -y is for visualizing cacheus data")
        

    if args.cacheus_q:

        if alg_check(config, 'cacheus'):
            vu.visualize_data('-z', config)
        else:
            pretty.failure("cacheus algorithm not specified in config, this plotting flag -z is for visualizing cacheus data")
        
