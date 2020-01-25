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

    EJECT_START = "You can also EJECT"

    SORTING = {
        "type": ["move", "overcharge", "quick", "full", "reaction", "free", "downtime"],
        "quick": ["skirmish", "boost", "ram", "grapple", "quick tech", "hide"],
        "full": ["barrage", "full tech", "stabilize"]
    }

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
                name, delim, action = raw[0].strip().partition("(")
                self.name = name.strip().upper()
                self.action_type = action[:action.find(" ")].strip().lower().replace(")", "")
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

    def __eq__(self, other):
        if not isinstance(other, Action):
            return NotImplemented
        return (self.action_type == other.action_type and
                self.pilot == other.pilot and
                self.reserve == other.reserve and
                self.name == other.name)

    def __lt__(self, other):
        if not isinstance(other, Action):
            return NotImplemented
        # Action types match, sort by name
        if (self.action_type == other.action_type and
                self.reserve == other.reserve and
                self.pilot == other.pilot):
            # Prioritize sorting certain actions
            if self.action_type in Action.SORTING.keys():
                key = self.action_type
                if self.name.lower() in Action.SORTING[key]:
                    if other.name.lower() in Action.SORTING[key]:
                        return (Action.SORTING[key].index(self.name.lower()) <
                                Action.SORTING[key].index(other.name.lower()))
                    # self's name is prioritized but not other's, so self is less
                    else:
                        return True
                # other's name is prioritized but not self's, so other is less
                elif other.name in Action.SORTING[key]:
                    return False
            else:
                return self.name < other.name
        # Action type matches, sort pilot > reserve > rest
        elif self.action_type == other.action_type:
            if not self.reserve and other.reserve:
                return True
            elif not self.pilot and other.pilot:
                return True
        # Sort by action type
        return (Action.SORTING['type'].index(self.action_type) <
                Action.SORTING['type'].index(other.action_type))
