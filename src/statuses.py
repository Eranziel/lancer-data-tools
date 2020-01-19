# /bin/python3
# -*- utf-8 -*-

from parseutil import *


class Status:
    """
    Class for status/condition data.
    NECESSARY PREP WORK:
    * None yet.
    """

    START = ["STATUSES AND CONDITIONS\n",
             "During combat, characters often inflict and receive",
             "Actions, talents, systems, and other effects can all inflict"]
    END = ["STUNNED\n",
           "STUNNED mechs cannot OVERCHARGE, move, or take any actions",
           "STUNNED mechs have a maximum of 5 EVASION, and automatically"]

    PREFIX = "sts_"

    STATUS = "STATUSES\n"
    CONDITION = "CONDITIONS\n"

    def __init__(self, raw="", status=True):
        self.id = ""
        self.name = ""
        if status:
            self.type = "Status"
        else:
            self.type = "Condition"
        self.effect = []

        if raw != "":
            self.parse_text(raw)

    def parse_text(self, raw):
        self.name = raw[0].strip()
        self.id = gen_id(Status.PREFIX, self.name)

        # Get the effect
        self.effect = combine_lines(raw[1:])

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "type": self.type,
                "effects": self.effect}
