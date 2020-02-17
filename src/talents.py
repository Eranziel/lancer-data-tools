#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class Talent:
    """
    Class for talent data
    NECESSARY PREP-WORK:
    * Ensure each talent is preceded and followed by one empty line.
    * Fix broken newlines - make sure each Rank starts on a new line.
    * Grease Monkey: Rank 3 is numbered 2.
    """

    START = ["Spaceborn\n",
             "You’re adept at planting your feet",
             "Rank 1: Home in the Void"]
    END = ["- Field Repair (full action): Heal",
           "Rank 3: Rodeo Master",
           "When you exit your mech, your pilot gains"]

    PREFIX = "t_"

    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.description = ""
        # list of 3 dicts with keys 'name' and 'description'
        self.ranks = [dict([("name", ""), ("description", "")]) for i in range(3)]

        if raw_text:
            self.parse_raw_text(raw_text)

    def __str__(self):
        output = "\n============== TALENT ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\ndesc: {self.description}\n"
        output += f"\nranks:"
        for r in self.ranks:
            output += f"\n    name: {r['name']}"
            output += f"\n    desc: {r['description']}"
        return output

    def parse_raw_text(self, raw_text):
        """
        Parse the text for a pilot talent.
        @param raw_text: [str]: The text to parse.
        @return: None.
        """
        RANK = ["Rank 1: ",
                "Rank 2: ",
                "Rank 3: "]

        name_line = -1
        rank_start = [-1, -1, -1]
        for i in range(len(raw_text)):
            line = raw_text[i].strip()
            # Name is the first non-empty line
            if self.name == "" and line != "":
                self.name = line.upper()
                self.id = gen_id(Talent.PREFIX, self.name)
                # self.id = "t_"+self.name.lower().replace(" ", "_")
                name_line = i
            # Don't look for the rest until the name is found
            elif 0 <= name_line < i:
                # Find the lines which contain the rank names
                for j in range(len(RANK)):
                    if RANK[j] in line:
                        rank_start[j] = i
        # Description starts line after name, and ends at line before rank 1.
        self.description = combine_lines(raw_text[name_line+1:rank_start[0]])
        # Get ranks text
        for i in range(len(rank_start)):
            line = raw_text[rank_start[i]].strip()
            self.ranks[i]["name"] = line.split(":")[1].strip().upper()

            r_desc = ""
            # Get the line the next rank starts on.
            if i < len(rank_start)-1:
                next_r = rank_start[i+1]
            # Last rank ends at the end of the raw text.
            else:
                next_r = len(raw_text)
            self.ranks[i]["description"] = combine_lines(raw_text[rank_start[i]+1:next_r])

    def set_id(self, new_id):
        self.id = new_id

    def set_name(self, new_name):
        self.name = new_name

    def set_desc(self, new_desc):
        self.description = new_desc

    def set_rank(self, idx, rank_name, rank_desc):
        self.ranks[idx]["name"] = rank_name
        self.ranks[idx]["description"] = rank_desc

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "ranks": self.ranks}