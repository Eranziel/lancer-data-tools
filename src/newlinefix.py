#!/bin/python3
# -*- utf-8 -*-

"""Adds missing newlines to raw text."""

import sys

if __name__ == "__main__":
    print(f"{sys.argv}")
    in_file = sys.argv[1]
    out_file = sys.argv[2]

    # Read raw file into memory - need to watch memory usage
    try:
        with open(in_file, 'r', encoding='utf-8') as rawFile:
            try:
                with open(out_file, 'w', encoding='utf-8') as outFile:
                    for line in rawFile:
                        period = line.rfind(".")
                        if period != -1 and len(line) > period+1:
                            if line[period+1].isalpha():
                                print(f"Fixing newline on: {line}")
                                outFile.write(line[:period+1] + "\n")
                                outFile.write(line[period+1:])
                                continue
                        outFile.write(line)
            except FileNotFoundError:
                print(f"Output file {out_file} not found.")
                exit(1)
    except FileNotFoundError:
        print(f"Input file {in_file} not found.")
        exit(1)
