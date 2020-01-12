#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class Tag:
    """Class for tag data"""

    START = ["HARM TYPE\n",
             "Weapons deal one of four types of damage - ",
             "- BURN X: On a hit, this weapon deals X"]
    END = ["- PERSONAL ARMOR: This gear offers protection in combat, ",
           "- GEAR: This is a tool, piece of equipment, ",
           "- SIDEARM: This weapon can be used to FIGHT "]

    FILT_IGN = ["PATTERNS\n", "OTHER WEAPON TAGS\n"]

    PREFIX = "tg_"

    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.description = ""
        self.filter_ignore = False

        if raw_text:
            self.parse_raw_text(raw_text)

    def __str__(self):
        output = "\n============== TAG ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: |{self.name}|"
        output += f"\ndesc: {self.description}"
        output += f"\nfilter: {self.filter_ignore}"
        return output

    def parse_raw_text(self, raw_text):
        """
        Parse the text for a gear tag.
        @param raw_text: [str]: The text to parse.
        @return: None.
        """
        VAL = " X", " {VAL}"

        # Strip out the bullet
        parts = raw_text[2:].split(":")
        self.name = parts[0]
        # Ugly hack of a special case for AP.
        if "(AP)" in self.name:
            self.id = gen_id(Tag.PREFIX,
                             "AP")
        else:
            self.id = gen_id(Tag.PREFIX, self.name)
        self.id = self.id.replace("_x", "")
        # self.id = "tg_"+self.name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("_x", "")
        if VAL[0] in self.name:
            # print(f"Replace {VAL[0]} in {self.name} with {VAL[1]}")
            self.name = self.name.replace(VAL[0], VAL[1])
        self.description = parts[1].strip()
        if VAL[0] in self.description:
            self.description = self.description.replace(VAL[0], VAL[1])

    def set_id(self, new_id):
        self.id = new_id

    def set_name(self, new_name):
        self.name = new_name

    def set_desc(self, new_desc):
        self.description = new_desc

    def set_filter(self, new_filter):
        self.filter_ignore = new_filter

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "filter_ignore": self.filter_ignore}
