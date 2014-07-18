#!/usr/bin/env python2

import threading
import csv
from test_hardware import *
import numpy as np
import pickle


"""
A class to make it simple to collect tagged csv data from the OpenBCI board.
It will keep track of data and store it in a csv file.

See OpenBCIBoard and FeatureExtractor for more info.
"""


class OpenBCICollector(object):

    def __init__(self,  buffer_size=250,
                 fname = 'collect.csv',
                 port='/dev/ttyACM0', baud=115200):
        self.board = OpenBCIBoard(port, baud)
        self.fname = fname
        self.buffer_size = buffer_size
        self.counter = 0
        self.file = open(self.fname, "w")
        self.csv_writer = csv.writer(self.file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        
        
    def collect(self):       

        self.board.start(self.handle_sample)
        self.file.close()

    def handle_sample(self, sample):

        if self.counter < self.buffer_size:
          self.csv_writer.writerow(sample.channels)
          self.counter +=  1 
        else:
          self.board.stop_streaming()
          self.counter = 0
        #print(sample.channels)


print("starting")

collector = OpenBCICollector()
collector.collect()


print("done")

