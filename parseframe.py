#!/bin/python3

"""Parses data for mech frames"""

import sys
import json
# import asyncio

from frame import Frame

class DataOutput:
    def __init__(self, datafile = None):
        self.datafile = datafile
    
    def out(self, data):
        for line in data:
            if self.datafile is not None:
                try:
                    with open(self.datafile, 'a') as f:
                        f.write(line)
                except:
                    print("Error opening file {}".format(self.datafile))
                    exit(1)
            else:
                print(line)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw = sys.argv[1]
        print("Input file: {}".format(raw))

        if len(sys.argv) > 2:
            data = sys.argv[2]
            print("Output file: {}".format(data))
        else:
            data = None
            print("No output file, output to console.")
        dataOutput = DataOutput(data)

        try:
            with open(raw) as rawf:
                for line in rawf:
                    dataOutput.out(line)
        except:
            print("Error reading file {}".format(raw))
    else:
        print("No input given.")
