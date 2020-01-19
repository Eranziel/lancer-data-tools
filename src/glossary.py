#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class GlossaryItem:
    """
    Class for combat glossary entries.
    """

    START = ["COMBAT TERMINOLOGY\n",
             "ARMOR: All kinetic, energy, and explosive",
             "BONUS DAMAGE: Extra damage – kinetic"]
    END = ["SPEED: The number of spaces a character",
           "TECH ATTACK: The statistic used to make",
           "THREAT: The maximum range at which"]

    def __init__(self, raw_text=None):
        self.name = ""
        self.description = ""

        if raw_text:
            self.parse_raw_text(raw_text)

    def __str__(self):
        output = "\n============== GLOSSARY ===================="
        output += f"\nname: {self.name}"
        output += f"\ndesc: {self.description}"
        return output

    def parse_raw_text(self, raw_text):
        """
        Parse the text for a pilot skill.
        @param raw_text: str: The text to parse.
        @return: None.
        """
        self.name, delim, self.description = raw_text.partition(":")
        self.name = self.name.strip()
        self.description = self.description.strip()

    def set_name(self, new_name):
        self.name = new_name

    def set_desc(self, new_desc):
        self.description = new_desc

    def to_dict(self):
        return {"name": self.name,
                "description": self.description}
