#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class Reserve:
    """
    Class for reserves.
    """

    START = ["RESOURCES\n",
             "1-2 Access",
             "A keycard, invite, bribes or insider"]
    END = ["The ability to start the mission by dropping",
           "19-20 NHP Assistant ",
           "A non-human person (NHP) – an advanced"]

    PREFIX = "reserve_"

    def __init__(self, raw_text=None, r_type=None):
        self.id = ""
        self.name = ""
        self.type = ""
        self.label = ""
        self.description = ""

        if r_type:
            self.type = r_type

        if raw_text:
            self.parse_raw_text(raw_text)

    def __str__(self):
        output = "\n============== RESERVE ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\ntype: {self.type}"
        output += f"\nlabel: {self.label}"
        output += f"\ndesc: {self.description}"
        return output

    def parse_raw_text(self, raw):
        """
        Parse the text for a reserve.
        @param raw: str: The text to parse.
        @return: None.
        """
        self.name = raw[0][raw[0].find(" "):].strip()
        self.id = gen_id(Reserve.PREFIX, self.name)
        self.description = raw[1].strip()

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "type": self.type,
                "label": self.label,
                "description": self.description}
