#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class NPCClass:
    """
    Class for NPC classes.
    NECESSARY PREP WORK:
    * Separate each NPC class with an empty line.
    * 1 empty line before and after "Base Systems" and "Optional Systems".
    """

    START = ["Ace\n",
             "Striker\n",
             "The first person to embody the “Ace” archetype was Aisling"]
    END = ["Winged\n",
           "Trait\n",
           "The Monstrosity may fly whenever it moves,"]

    PREFIX = "npcc_"

    TACTICS_TITLE = "Tactics\n"
    STAT_TITLE = "Stats\n"
    TIER = ("Tier 1\n", "Tier 2\n", "Tier 3\n")
    STATS = dict([
        ("armor", "armor"),
        ("hp", "hp"),
        ("evasion", "evade"),
        ("e-defense", "edef"),
        ("heat cap", "heatcap"),
        ("speed", "speed"),
        ("sensors", "sensor"),
        ("save target", "save"),
        ("hull", "save"),
        ("agility", "agility"),
        ("systems", "systems"),
        ("engineering", "engineering"),
        ("size", "size"),
        ("activations", "activations")
    ])

    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.role = ""
        self.info = dict([
            ("flavor", ""),
            ("tactics", "")
        ])
        arr = [0 for i in range(3)]
        self.stats = dict([
            ("armor", arr.copy()),
            ("hp", arr.copy()),
            ("evade", arr.copy()),
            ("edef", arr.copy()),
            ("heatcap", arr.copy()),
            ("speed", arr.copy()),
            ("sensor", arr.copy()),
            ("save", arr.copy()),
            ("hull", arr.copy()),
            ("agility", arr.copy()),
            ("systems", arr.copy()),
            ("engineering", arr.copy()),
            ("size", arr.copy()),
            ("activations", [1 for i in range(3)])
        ])
        self.base_feat = []
        self.opt_feat = []
        self.power = 100

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC CLASS ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\nrole: {self.role}"
        output += f"\nflavor: {self.info['flavor']}"
        output += f"\ntactics: {self.info['tactics']}"
        output += f"\nstats:"
        for stat in self.stats:
            output += f"\n   {stat}: {self.stats[stat]}"
        output += f"\nbase features:"
        for feat in self.base_feat:
            output += f"\n   {feat}: {self.base_feat[feat]}"
        output += f"\noptional features:"
        for feat in self.opt_feat:
            output += f"\n   {feat}: {self.opt_feat[feat]}"
        output += f"\npower: {self.power}"
        return output

    def parse_text(self, raw):
        """
        Parse the raw text for an NPC class.
        @param raw: [str]: The raw text to parse.
        @return: None.
        """
        self.name = raw[0].strip().upper()
        self.id = gen_id(NPCClass.PREFIX, self.name)
        self.role = raw[1].strip().lower()

        tactics = 0
        stats = 0
        for i in range(len(raw)):
            if raw[i] == NPCClass.TACTICS_TITLE:
                tactics = i
            if raw[i] == NPCClass.STAT_TITLE:
                stats = i
        self.info["flavor"] = combine_lines(raw[2:tactics])
        self.info["tactics"] = combine_lines((raw[tactics:stats]))

        # Parse stats
        tier = -1
        for line in raw[stats:]:
            # Check whether we are in a new tier's stats
            for i in range(len(NPCClass.TIER)):
                if line == NPCClass.TIER[i]:
                    tier = i
                    break
            if ":" in line:
                parts = line.split(":")
                self.stats[NPCClass.STATS[parts[0].strip().lower()]][tier] = parts[1].strip()

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "role": self.role,
                "info": self.info,
                "stats": self.stats,
                "base_features": self.base_feat,
                "optional_features": self.opt_feat,
                "power": self.power}
