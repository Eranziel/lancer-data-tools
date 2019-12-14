#!python

"""Parses data for mech frames"""

import argparse
import json
# import asyncio

from frame import Frame
from talents import Talent
from dataoutput import DataOutput

talentDelim = ["TALENTS\n", "GEAR AND SYSTEMS\n"]
pilotGearDelim = ["PILOT GEAR\n", "MECHS\n"]

rawLines = []


def check_section(start, end):
    start_idx = -1
    end_idx = -1
    for i in range(len(rawLines)):
        sfound = True
        efound = True
        for j in range(len(start)):
            if start_idx < 0:
                sfound = sfound and rawLines[i+j].startswith(start[j])
            if end_idx < 0:
                efound = efound and rawLines[i+j].startswith((end[j]))
            if not sfound and not efound:
                break

        # If lines i through i+j all match start, record the starting line.
        if sfound and start_idx < 0:
            start_idx = i
        if efound and end_idx < 0:
            end_idx = i+j
        if start_idx >= 0 and end_idx >= 0:
            return start_idx, end_idx


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
        print(f"Raw input file {rawFile} not found.")
        exit(1)

    # Parse the text
    if args.talents:
        s, e = check_section(Talent.START, Talent.END)
        print(f"Talents start: {s}, end: {e}")
        rawTalents = rawLines[s:e+1]
        divTalents = []
        prev = 0
        for i in range(len(rawTalents)):
            if rawTalents[i] == "\n":
                divTalents.append(rawTalents[prev:i])
                prev = i+1

    # Output results
    if args.talents:
        talents = []
        for t in divTalents:
            talents.append(Talent(t))
            # print(t)
            # print("\n\n")
        # talentsOut.write(rawTalents)
else:
    print("No input given.")
