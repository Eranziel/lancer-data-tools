#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class NPCTemplate:
    """
    Class for NPC templates.
    """

    START = ["Commander\n",
             "Commanders operate on a grand scale, controlling",
             "Template Features\n"]
    END = ["Treads or Hover",
           "Trait",
           "The Vehicle ignores difficult terrain."]

    PREFIX = "npct_"

    TEMP_FEAT = "template features\n"

    GRUNT = "GRUNT"
    VET = "VETERAN"
    ELITE = "ELITE"
    CMDR = "COMMANDER"
    ULTRA = "ULTRA"

    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.description = ""
        self.base_feat = []
        self.opt_feat = []
        self.power = 20

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC TEMPLATE ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\ndesc: {self.description}"
        for feat in self.base_feat:
            output += f"\n   {feat}: {self.base_feat[feat]}"
        output += f"\noptional features:"
        for feat in self.opt_feat:
            output += f"\n   {feat}: {self.opt_feat[feat]}"
        output += f"\npower: {self.power}"
        return output

    def parse_text(self, raw):
        self.name = raw[0].strip().upper()
        self.id = gen_id(NPCTemplate.PREFIX, self.name)
        tf = -1
        for i in range(len(raw)):
            if raw[i].lower() == NPCTemplate.TEMP_FEAT:
                tf = i
        self.description = combine_lines(raw[1:tf])

        if self.name == NPCTemplate.GRUNT:
            self.power = -75
        if self.name == NPCTemplate.VET or self.name == NPCTemplate.CMDR:
            self.power = 50
        if self.name == NPCTemplate.ELITE:
            self.power = 100
        if self.name == NPCTemplate.ULTRA:
            self.power = 300

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "base_features": self.base_feat,
                "optional_features": self.opt_feat,
                "power": self.power}
