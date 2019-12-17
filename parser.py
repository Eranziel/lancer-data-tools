#!python

"""Parses data for mech frames"""

import argparse
import json
# import asyncio

from frame import Frame
from talents import Talent
from dataoutput import DataOutput

rawLines = []


def check_section(start, end):
    start_idx = -1
    end_idx = -1
    for i in range(len(rawLines)):
        sfound = True
        efound = True
        for j in range(len(start)):
            # If lines i through i+j all match start, record the starting line.
            if start_idx < 0:
                sfound = sfound and rawLines[i+j].startswith(start[j])
            if end_idx < 0:
                efound = efound and rawLines[i+j].startswith((end[j]))
            # Stop if a line doesn't match either the start or end delimeters.
            if not sfound and not efound:
                break

        if sfound and start_idx < 0:
            start_idx = i
        if efound and end_idx < 0:
            end_idx = i+j
        if start_idx >= 0 and end_idx >= 0:
            return start_idx, end_idx
    print(f"There was a problem! s{start_idx}, e{end_idx}")


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

    # Read raw file into memory - need to watch memory usage
    try:
        with open(args.raw, 'r', encoding='cp1252') as rawFile:
            rawLines = rawFile.readlines()
    except FileNotFoundError:
        print(f"Raw input file {rawFile} not found.")
        exit(1)

    if args.talents:
        # Create data output
        dOut = DataOutput(args.talents)
        rawTalents = []
        inTalents = False

        # Parse the text
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
        talents = []
        j = []
        for t in divTalents:
            talents.append(Talent(t))
        for t in talents:
            j.append(t.to_dict())
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))
    if args.pilot_gear:
        dOut = DataOutput(args.pilot_gear)
        rawPilotGear = []
        inPilotGear = False
