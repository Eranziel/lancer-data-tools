#!python

"""Parses data for mech frames"""

import argparse
import json
# import asyncio

from frame import Frame
from dataoutput import DataOutput

talentDelim = ["TALENTS\n", "GEAR AND SYSTEMS\n"]
pilotGearDelim = ["PILOT GEAR\n", "MECHS\n"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--talents", nargs="?", const="stdout",
                        help="Generate talents JSON. Output to TALENTS, or stdout if not specified.")
    parser.add_argument("-p", "--pilot-gear", nargs="?", const="stdout",
                        help="Generate pilot gear JSON. Output to PILOT_GEAR, or stdout if not specified.")
    parser.add_argument("-f", "--frames", nargs="?", const="stdout",
                        help="Generate frame JSON. Output to FRAMES, or stdout if not specified.")
    parser.add_argument("raw", help="raw text input file")
    args = parser.parse_args()

    # Create data outputs for each selected output file type
    if args.talents:
        talentsOut = DataOutput(args.talents)
        rawTalents = []
        inTalents = False
    if args.pilot_gear:
        pilotGearOut = DataOutput(args.pilot_gear)
        rawPilotGear = []
        inPilotGear = False

    # Read raw file into memory - need to watch memory usage
    try:
        with open(args.raw, 'r') as rawFile:
            rawLines = rawFile.readlines()
    except FileNotFoundError:
        print(f"Raw input file {raw} not found.")
        exit(1)

    # Parse the text
    for i in range(len(rawLines)):
        line = rawLines[i]
        if args.talents:
            if not inTalents and line == talentDelim[0]:
                inTalents = True
                rawTalents.append(line)
            elif inTalents and line == talentDelim[1]:
                inTalents = False
            elif inTalents:
                rawTalents.append(line)

    # Output results
    if args.talents:
        talentsOut.write(rawTalents)
else:
    print("No input given.")
