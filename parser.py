#!python

"""Parses data for mech frames"""

import argparse
import json
# import asyncio

from frame import Frame
from dataoutput import DataOutput

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
    if not args.raw:
        print("No input file specified, exiting.")
        exit(1)
    if args.talents:
        talentsOut = DataOutput(args.talents)
    if args.pilot_gear:
        pgearOut = DataOutput(args.pilot_gear)

    try:
        with open(raw) as rawFile:
            compendium = []
            npcs = []
            compFound = False
            npcsFound = False
            for line in rawFile:
                if compFound is False and line == "Compendium\n":
                    compFound = True
                    compendium.append(line)
                elif compFound is True and line == "Game Master's Guide\n":
                    compFound = False
                elif compFound is True:
                    compendium.append(line)
                elif npcsFound is False and line == "ACE\n":
                    npcsFound = True
                    npcs.append(line)
                elif npcsFound is True:
                    npcs.append(line)
                else:
                    pass

            dataOutput.out(compendium)

    except:
        print("Error reading file {}".format(raw))
else:
    print("No input given.")
