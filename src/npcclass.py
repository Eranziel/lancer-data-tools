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

    ROLES = ["striker\n",
             "controller\n",
             "artillery\n",
             "defender\n",
             "support\n",
             "biological\n"]

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
        ("hull", "hull"),
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
        for stat in self.stats.keys():
            output += f"\n   {stat}: {self.stats[stat]}"
        output += f"\nbase features:"
        for feat in self.base_feat:
            output += f"\n   {feat}"
        output += f"\noptional features:"
        for feat in self.opt_feat:
            output += f"\n   {feat}"
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

        tactics = -1
        stats = -1
        for i in range(len(raw)):
            if raw[i] == NPCClass.TACTICS_TITLE:
                tactics = i
            if raw[i] == NPCClass.STAT_TITLE:
                stats = i
        if tactics == -1:
            tactics = stats
        self.info["flavor"] = combine_lines(raw[2:tactics])
        if tactics != stats:
            self.info["tactics"] = combine_lines((raw[tactics+1:stats]))

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
                key = NPCClass.STATS[parts[0].strip().lower()]
                val = parts[1].strip()
                # Size is special, stored as a 2D array.
                if key == "size":
                    parts = [val]
                    if " or " in val:
                        p1, d, p2 = val.partition(" or ")
                        parts = [p1, p2]
                        for p in parts:
                            if "," in p:
                                p1, d, p2 = p.partition(",")
                                parts.insert(parts.index(p), p1)
                                parts.insert(parts.index(p), p2)
                                parts.remove(p)
                    val = []
                    for p in parts:
                        p = p.strip()
                        if p.isdecimal():
                            val.append(int(p))
                        elif p == "1/2":
                            val.append(0.5)
                        else:
                            val.append(p)
                    self.stats[key][tier] = val
                else:
                    val = val.strip().replace("+", "").replace("–", "-")
                    if val.replace("-", "").isdecimal():
                        self.stats[key][tier] = int(val)
                    elif val.replace("-", "").isnumeric():
                        self.stats[key][tier] = float(val)
                    else:
                        print(f"NPC {self.name}, stat {key}: {val}")
                        self.stats[key][tier] = val

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "role": self.role,
                "info": self.info,
                "stats": self.stats,
                "base_features": self.base_feat,
                "optional_features": self.opt_feat,
                "power": self.power}
