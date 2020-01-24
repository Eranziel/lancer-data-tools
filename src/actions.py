#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class Action:
    """
    Class for player actions.
    NECESSARY PREP-WORK:
    * Ensure there is an empty line before each type of action (down time,
    quick, full, etc...)
    """

    START = ["DOWNTIME ACTIONS\n",
             "Downtime actions represent specific activities undertaken by",
             "Unlike skill checks, downtime actions have specific outcomes"]
    END = ["On each of your subsequent turns, you can continue to choose",
           "RELOAD (QUICK ACTION)\n",
           "When you RELOAD, you reload one Pilot Weapon with the LOADING"]

    PREFIX = "act_"

    DOWNTIME = ("DOWNTIME ACTIONS", "downtime")
    QUICK = ("QUICK ACTIONS", "quick")
    FULL = ("FULL ACTIONS", "full")
    OTHER = ("OTHER ACTIONS", "")
    REACTIONS = ("REACTIONS", "reaction")
    PILOT = ("PILOT ACTIONS", "")

    def __init__(self, raw_text=None, action="", pilot=False, reserve=False):
        self.id = ""
        self.name = ""
        self.action_type = action.lower()
        self.description = ""
        self.detail = ""
        self.pilot = pilot
        self.reserve = reserve

        if raw_text is not None:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== ACTION ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\ntype: {self.action_type}"
        output += f"\ndesc: {self.description}"
        output += f"\ndetail: {self.detail}"

    def parse_text(self, raw):
        if self.action_type == "":
            if "(" in raw[0]:
                name, delim, action = raw[0].partition("(")
                self.name = name.strip().upper()
                self.action_type = action.replace(")", "").strip().lower()
            else:
                self.name = raw[0].strip().upper()
        else:
            self.name = raw[0].strip().upper()
        if self.name == "OVERCHARGE":
            self.action_type = self.name.lower()
        if self.name == "FREE ACTIONS":
            self.name = "FREE ACTION"
            self.action_type = "free"
        self.id = gen_id(Action.PREFIX, self.name)
        self.detail = combine_lines(raw[1:])

    def to_dict(self):
        d = {"id": self.id,
             "name": self.name,
             "action_type": self.action_type,
             "description": self.description,
             "detail": self.detail}
        if self.pilot:
            d["pilot"] = self.pilot
        if self.reserve:
            d["reserve"] = self.reserve
        return d
