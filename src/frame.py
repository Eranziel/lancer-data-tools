#!/bin/python3
# -*- utf-8 -*-

from parseutil import *
from licensegear import Weapon


class Frame:
    """
    Class for frame data.
    NECESSARY PREP-WORK:
    * Make sure each frame is preceded by an empty line.
    * Make sure there are no empty lines in the frame block - from frame name to
      the end of the license table must be continuous.
    * Make sure there is an empty line between the frame block and the first
      licensed gear.
    * Add a line containing "---\n" to CORE systems between:
      * Description and passive name, if applicable.
    * In BLACKBEARD, reformat license table to match other frames.
    * In LANCASTER, plasma torch missing from license table.
    * In MOURNING CLOAK, the Exposed Singularity reaction is missing.
    * BARBAROSSA is missing the Pressure Plating trait.
    * In BARBAROSSA, add this line after the name line of Siege Cannon:
        [3d6 explosive damage]
    """

    START = ["SSC\n",
             "ATLAS\n",
             "Striker\n"]
    END = ["Wind Stance: This weapon gains reliable 2, threat 2",
           "---\n",
           "Forged in the fire of a dying star and perfectly balanced"]

    PREFIX = "mf_"

    LICENSE = ("License", "License I: ", "License II: ", "License III: ")
    CORE_STATS = "CORE STATS\n"
    TRAITS = "TRAITS\n"
    MOUNTS = "MOUNTS\n"
    CORE = "CORE SYSTEM\n"
    CORE_ACTIVE = "Active (1CP)"
    INTEGRATED = "Integrated Mount: "

    STATS = dict([
        ("size", "size"),
        ("armor", "armor"),
        ("hp", "hp"),
        ("evasion", "evasion"),
        ("e-defense", "edef"),
        ("heat cap", "heatcap"),
        ("repair cap", "repcap"),
        ("sensors", "sensor_range"),
        ("tech attack", "tech_attack"),
        ("save target", "save"),
        ("speed", "speed"),
        ("system points", "sp"),
        ("sp", "sp")
    ])

    def __init__(self, raw_text=None):
        """
        Initializer for Frame. Can either create a blank instance, or parse
        text.
        @param raw_text: [str]: raw text for the frame
        """
        self.id = ""
        self.source = ""
        self.name = ""
        self.mechtype = []
        self.y_pos = ""
        self.description = ""
        self.mounts = []
        self.stats = dict([
            ("size", 0),
            ("armor", 0),
            ("hp", 0),
            ("evasion", 0),
            ("edef", 0),
            ("heatcap", 0),
            ("repcap", 0),
            ("sensor_range", 0),
            ("tech_attack", 0),
            ("save", 0),
            ("speed", 0),
            ("sp", 0)
        ])
        self.traits = []
        self.core_system = dict([
            ("name", ""),
            ("description", ""),
            ("active_name", ""),
            ("active_effect", ""),
            ("tags", [])
        ])
        self.data_type = "frame"
        self.aptitude = dict()
        # 2D list for what belongs in which level of the frame's license.
        self.license = [[] for i in range(3)]

        if raw_text is not None:
            # print(f"Frame from hunk:\n{raw_text}")
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== FRAME ===================="
        output += f"\nid: {self.id}"
        output += f"\nsource: {self.source}"
        output += f"\nname: {self.name}"
        output += f"\ntype: {self.mechtype}"
        output += f"\ndesc: {self.description}"
        output += f"\nlicense: {self.license}"
        output += f"\ny_pos: {self.y_pos}"
        output += f"\nmounts: {self.mounts}"
        output += f"\nstats:"
        for stat in self.stats:
            output += f"\n   {stat}: {self.stats[stat]}"
        output += f"\ntraits:"
        for trait in self.traits:
            output += f"\n   {trait}"
        output += f"\ncore:"
        for key in self.core_system:
            output += f"\n   {key}: {self.core_system[key]}"
        output += f"\ndata_type: {self.data_type}"
        output += f"\naptitude: {self.aptitude}"
        return output

    def parse_text(self, raw_text):
        """
        Parse the raw text for a mech frame.
        @param raw_text: [str]: The raw text to parse.
        @return: None.
        """
        self.source = raw_text[0].strip().upper()
        self.name = raw_text[1].strip().upper()
        # Generate the id from the name
        self.id = gen_id(Frame.PREFIX, self.name)

        # Raw text indices for subsections
        desc = lic = stats = traits = mounts = core = 0

        # If the line after the name is only one word, it's the role
        if len(raw_text[2].split(" ")) == 1:
            desc = 3
        else:
            desc = 2
        # Find the start of each subsection.
        for i in range(len(raw_text)):
            if lic == 0 and raw_text[i].startswith(Frame.LICENSE[0]):
                lic = i
            elif stats == 0 and raw_text[i] == Frame.CORE_STATS:
                stats = i
            elif traits == 0 and raw_text[i] == Frame.TRAITS:
                traits = i
            # elif sp == 0 and raw_text[i].startswith(Frame.SP):
            #     sp = i
            elif mounts == 0 and raw_text[i] == Frame.MOUNTS:
                mounts = i
            elif core == 0 and raw_text[i] == Frame.CORE:
                core = i
        # If no licensed gear was found, get rid of the 2nd dimension.
        if lic == 0:
            self.license = []

        # If no role was found, its role is "Balanced"
        if desc == 2:
            self.mechtype.append("Balanced")
        else:
            for t in raw_text[2].split("/"):
                self.mechtype.append(t.strip())

        # Description starts after the role and goes to CORE_STATS.
        self.description = combine_lines(raw_text[desc:stats], check_horus=True)

        # Stats go until traits
        for stat in raw_text[stats+1:traits]:
            tokens = stat.split(":")
            key = Frame.STATS[tokens[0].strip().lower()]
            val = tokens[1].strip()
            if val == "1/2":
                self.stats[key] = 0.5
            else:
                self.stats[key] = int(val)

        # Traits go until Mounts
        traits_lines = raw_text[traits+1:mounts]
        i = 0
        while i < len(traits_lines):
            # Each trait is a dict with two keys: name and description.
            curr_trait = dict([
                ("name", ""),
                ("description", "")
            ])
            curr_trait["name"] = traits_lines[i].strip()
            curr_trait["description"] = traits_lines[i+1].strip()
            self.traits.append(curr_trait)
            i += 2

        # Mounts go until core system
        for mount in raw_text[mounts+1:core]:
            mount = mount.strip().replace("- ", "")
            end = mount.lower().find(" mount")
            if end != -1:
                self.mounts.append(mount[:end].title())
            else:
                self.mounts.append(mount.title())
        for i in range(len(self.mounts)):
            if self.mounts[i] == "Flexible":
                self.mounts[i] = "Flex"

        # Core system goes until the end
        # Find all of the lines that are all caps - these are the passive
        #   and active names.
        if lic != 0:
            core_lines = raw_text[core+1:lic]
        else:
            core_lines = raw_text[core+1:]
        act_start = -1
        pass_start = -1
        integrated_start = -1
        # Find the section for the CORE active.
        for i in range(len(core_lines)):
            if core_lines[i].startswith(Frame.CORE_ACTIVE):
                act_start = i-1
            if core_lines[i] == "---\n":
                pass_start = i+1
            if core_lines[i].startswith(Frame.INTEGRATED):
                integrated_start = i
        act_sec = core_lines[act_start:]
        if pass_start != -1:
            pass_sec = core_lines[pass_start:act_start]
        else:
            pass_sec = []
        # First line is always the name of the core system
        self.core_system["name"] = core_lines[0].strip()
        # If the next line isn't a passive/active effect name, then the core
        #   system has a description.
        if pass_start != 1 and act_start != 1:
            if pass_start != -1:
                desc_sec = core_lines[1:pass_start-1]
            elif integrated_start != -1:
                desc_sec = core_lines[1:integrated_start]
            else:
                desc_sec = core_lines[1:act_start]
            self.core_system["description"] = combine_lines(desc_sec)
        # If the core system has a passive effect, parse it.
        if pass_start != -1:
            self.core_system["passive_name"] = pass_sec[0].strip()
            self.core_system["passive_effect"] = ""
            self.core_system["passive_effect"] = combine_lines(pass_sec[1:])
        # If the core system has an integrated mount, add it.
        if integrated_start != -1:
            int_mech_name = gen_id(Weapon.PREFIX, self.name) + "_integrated"
            self.core_system["integrated"] = {"id": int_mech_name}
        # Parse the active name and effect
        self.core_system["active_name"] = act_sec[0].strip()
        # Line after the active name is the tags for the active effect
        self.parse_tags(act_sec[1].strip())
        # Lines after the tags is the active effect
        self.core_system["active_effect"] = combine_lines(act_sec[2:])

        # Sort licensed gear by license level
        for line in raw_text[lic:]:
            if line.startswith(Frame.LICENSE[1]):
                # Remove the rank identifier from the start of the line
                line = line[len(Frame.LICENSE[1]):]
                license_gear = [t.strip().lower() for t in line.split(",")]
                self.license[0] = license_gear
            elif line.startswith(Frame.LICENSE[2]):
                # Remove the rank identifier from the start of the line
                line = line[len(Frame.LICENSE[2]):]
                license_gear = [t.strip().lower() for t in line.split(",")]
                self.license[1] = license_gear
            elif line.startswith(Frame.LICENSE[3]):
                # Remove the rank identifier from the start of the line
                line = line[len(Frame.LICENSE[3]):]
                license_gear = [t.strip().lower() for t in line.split(",")]
                self.license[2] = license_gear

    def parse_tags(self, tagline):
        """
        Parse the tags from the given line of text.
        @param tagline: str: The line which contains tags.
        @return: None.
        """
        tags = tagline.split(",")
        for t in tags:
            if t != "-\n":
                # The "Active (1CP)" is not a proper tag - skip it.
                if t.endswith("(1CP)"):
                    continue
                words = t.strip().split(" ")
                if words[-1].isdecimal():
                    t_text = ""
                    for w in words[:-1]:
                        t_text += " "+w
                    d = {"id": "tg_"+(t_text.strip().lower().replace(" ", "_")),
                         "val": int(words[-1])}
                else:
                    d = {"id": "tg_"+(t.strip().lower().replace(" ", "_"))}
                if not is_duplicate_tag(d, self.core_system["tags"]):
                    self.core_system["tags"].append(d)

    def to_dict(self):
        return {"id": self.id,
                "source": self.source,
                "name": self.name,
                "mechtype": self.mechtype,
                "y_pos": self.y_pos,
                "description": self.description,
                "mounts": self.mounts,
                "stats": self.stats,
                "traits": self.traits,
                "core_system": self.core_system,
                "data_type": self.data_type,
                "aptitude": self.aptitude}
