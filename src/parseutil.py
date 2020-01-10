#!/bin/python3
# -*- utf-8 -*-


def gen_id(prefix, name):
    return prefix + name.strip().lower().replace(" ", "_").replace("/", "_").\
        replace("-", "_").replace("-", "_").replace("'", "").replace("\"", "").\
        replace("(", "").replace(")", "")
