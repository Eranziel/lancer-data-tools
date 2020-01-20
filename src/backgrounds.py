#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class Background:
    """
    Class for pilot background.
    """

    START = ["Celebrity\n",
             "Example triggers: Charm, Pull Rank,",
             "You were a figure in the public eye."]
    END = ["Worker\n",
           "Example triggers: Word on the Street,",
           "At the end of the day, empire only functions"]

    PREFIX = "pbg_"

    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.description = ""
        self.triggers = ""

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== BACKGROUND ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\ndesc: {self.description}"
        output += f"\ntriggers: {self.triggers}"
        return output

    def parse_text(self, raw):
        """
        Parse the text for quirks.
        @param raw: [str]: The text to parse.
        @return: None.
        """
        self.name = raw[0].strip().upper()
        self.id = gen_id(Background.PREFIX, self.name)

        self.triggers = raw[1].strip()
        self.description = combine_lines(raw[2:])

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "triggers": self.triggers}
