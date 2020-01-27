#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class NPCFeature:
    """
    Class for NPC features.
    """

    START = ["RESOURCES\n",
             "1-2 Access",
             "A keycard, invite, bribes or insider"]
    END = ["The ability to start the mission by dropping",
           "19-20 NHP Assistant ",
           "A non-human person (NHP) – an advanced"]

    PREFIX = "npcf_"

    def __init__(self, raw_text=None):
        pass
