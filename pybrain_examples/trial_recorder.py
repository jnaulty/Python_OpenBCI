#!/usr/bin/env python2

import threading
import csv
from open_bci import *
import numpy as np
import pickle
from csv_collector import *
import time


"""
A class to make it simple to collect tagged csv data from the OpenBCI board.
It will keep track of data and store it in a csv file.

See OpenBCIBoard and FeatureExtractor for more info.
"""


class TrialRecorder(object):

    def __init__( self, num_trials=5, trial_length_in_ms=125 ):
        #self.file_name = file_name
        self.num_trials = num_trials
        self.trial_length_in_ms = trial_length_in_ms 
        #self.file = open(self.file_name, "w")
        #self.csv_writer = csv.writer(self.file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        
        
    def collect(self):      

        for num in xrange(self.num_trials):
          print("starting")  
          file_name = 'test%d.csv' % (num) 
          collector = OpenBCICollector(
                        self.trial_length_in_ms, #buffer size
                        file_name, #file name
                        'COM9', #serial port connected to board
                        115200 #buad rate
                      )
          print("almost done")
          collector.collect()
          print("done")

        


# records trial and prints num of trials and sample time in seconds

trial_recorder = TrialRecorder(1, 250)
time_sec = trial_recorder.trial_length_in_ms / 250
print 'Recording %d trials for %d second(s)' % (trial_recorder.num_trials, time_sec) 
trial_recorder.collect()
