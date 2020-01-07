from parseutil import *


class Frame:
    """
    Class for frame data
    NECESSARY PREP-WORK:
    * Make sure each frame is preceded by an empty line.
    * Make sure there are no empty lines in the frame block - from frame name to
      the first licensed gear must be continuous.
    * Make sure there is an empty line between the frame block and the first
      licensed gear.
    * In the following frames, replace the line immediately preceding the stats
      with "CORE STATS\n": (this should be fixed in next release)
      * LANCASTER
      * VLAD
      * DEATH'S HEAD
      * METALMARK
      * MONARCH
      * MOURNING CLOAK
      * SWALLOWTAIL
      * PEGASUS
    * In VLAD, remove the ":" after "MOUNTS".

    NECESSARY POST-WORK:
    * y_pos and aptitude values need to be manually entered.
    * MANTICORE core system needs to be adjusted after parsing - parser misinterprets
      the description as the passive name.
    * Add <code></code> tags to RA text:
      * HYDRA's OROCHI Disarticulation description.
      * MANTICORE's Charged Exoskeleton description.
      * MINOTAUR's Metafold Maze description.
    """

    START = ["GENERAL MASSIVE SYSTEMS\n",
             "From Cradle to the stars, GMS: assured",
             "General Massive Systems - GMS for short - is the"]
    END = ["This system can only be used in the DANGER ZONE",
           "Expend a charge and choose a character adjacent to you",
           "\n"]

    PREFIX = "mf_"

    LICENSE = ("License:\n", "I. ", "II. ", "III. ")
    CORE_STATS = "CORE STATS\n"
    TRAITS = "TRAITS\n"
    SP = "SYSTEM POINTS:"
    MOUNTS = "MOUNTS\n"
    CORE = "CORE SYSTEM\n"
    CORE_ACTIVE = "Active (1CP)"
    INTEGRATED = "Integrated Mount:"

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
        ("system points", "sp")
    ])

    def __init__(self, raw_text=None):
        """
        Initializer for Frame. Can either create a blank instance, or parse
        text.
        @param raw_text: raw text for the frame
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
            # ("passive_name", ""),
            # ("passive_effect", ""),
            ("active_name", ""),
            ("active_effect", ""),
            ("tags", [])
        ])
        self.data_type = "frame"
        self.aptitude = dict()
        # 2D list for what belongs in which level of the frame's license.
        self.license = [[] for i in range(3)]

        if raw_text is not None:
            self.parse_frame(raw_text)

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

    def parse_frame(self, raw_text):
        name = raw_text[0].strip()
        spc = name.find(" ")
        # First line is the frame's name, minus the manufacturer acronym.
        self.name = name[spc:].strip()
        # Manufacturer acronym goes in source.
        self.source = name[:spc].strip()
        # Generate the id from the name
        self.id = gen_id(Frame.PREFIX, self.name)
        # self.id = "mf_"+self.name.strip().lower().replace(" ", "_").replace("\"", "").replace("'", "")

        # Raw text indices for subsections
        desc = lic = stats = traits = sp = mounts = core = 0
        if len(raw_text[1].split(" ")) == 1:
            desc = 2
        else:
            desc = 1

        # Find the start of each subsection.
        for i in range(len(raw_text)):
            if lic == 0 and raw_text[i] == Frame.LICENSE[0]:
                lic = i
            elif stats == 0 and raw_text[i] == Frame.CORE_STATS:
                stats = i
            elif traits == 0 and raw_text[i] == Frame.TRAITS:
                traits = i
            elif sp == 0 and raw_text[i].startswith(Frame.SP):
                sp = i
            elif mounts == 0 and raw_text[i] == Frame.MOUNTS:
                mounts = i
            elif core == 0 and raw_text[i] == Frame.CORE:
                core = i
        # If no licensed gear was found, get rid of the 2nd dimension.
        if lic == 0:
            self.license = []

        # If no role was found, its role is "Balanced"
        if desc == 1:
            self.mechtype.append("Balanced")
        else:
            for t in raw_text[1].split("/"):
                self.mechtype.append(t.strip())

        # Description starts after the role and goes to either LICENSE or CORE_STATS.
        if lic == 0:
            description = raw_text[desc:stats]
        else:
            description = raw_text[desc:lic]
        for line in description:
            if self.description == "":
                self.description = line.strip()
            else:
                self.description += "<br>"+line.strip()

        # Sort licensed gear by license level
        for line in raw_text[lic:lic+4]:
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

        # Stats go until traits
        for stat in raw_text[stats+1:traits]:
            tokens = stat.split(":")
            key = Frame.STATS[tokens[0].strip().lower()]
            val = tokens[1].strip()
            if val == "1/2":
                self.stats[key] = 0.5
            else:
                self.stats[key] = int(val)

        # Traits go until SP
        traits_lines = raw_text[traits+1:sp]
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

        # System points
        tokens = raw_text[sp].split(":")
        key = Frame.STATS[tokens[0].strip().lower()]
        val = tokens[1].strip()
        self.stats[key] = int(val)

        # Mounts go until core system
        for mount in raw_text[mounts+1:core]:
            end = mount.find(" MOUNT")
            self.mounts.append(mount[:end].title())
        for i in range(len(self.mounts)):
            if self.mounts[i] == "Flexible":
                self.mounts[i] = "Flex"

        # Core system goes until the end
        # Find all of the lines that are all caps - these are the passive
        #   and active names.
        core_lines = raw_text[core+1:]
        cap_lines = []
        act_name = 0
        # print("Core text:")
        for i in range(len(core_lines)):
            core_lines[i] = core_lines[i].strip()
            # print(f"   {i}: {core_lines[i]}")
            if i > 0 and core_lines[i].isupper():
                cap_lines.append(i)
            if core_lines[i].startswith(Frame.CORE_ACTIVE):
                act_name = i-1
        # print(f"cap_lines: {cap_lines}; act_name: {act_name}")
        # First line is always the name of the core system
        self.core_system["name"] = core_lines[0]
        # If the next line isn't a passive/active effect name, then the core
        #   system has a description.
        if cap_lines[0] != 1:
            for desc_line in core_lines[1:cap_lines[0]]:
                if not desc_line.startswith(Frame.INTEGRATED):
                    if self.core_system["description"] == "":
                        self.core_system["description"] = desc_line.strip()
                    else:
                        self.core_system["description"] += "<br>"+desc_line.strip()
        # If the core system has a passive effect, then the first capital line
        #   is not the same line as the core active name.
        if cap_lines[0] != act_name:
            # Check to see if it's an integrated mount.
            if core_lines[cap_lines[0]-1].startswith(Frame.INTEGRATED):
                int_mech_name = "mw_" + self.id[self.id.find("_")+1:] + "_integrated"
                self.core_system["integrated"] = {"id": int_mech_name}
            else:
                self.core_system["passive_name"] = core_lines[cap_lines[0]]
                pass_effect = core_lines[cap_lines[0]+1:act_name]
                self.core_system["passive_effect"] = ""
                for line in pass_effect:
                    if self.core_system["passive_effect"] == "":
                        self.core_system["passive_effect"] = line.strip()
                    else:
                        self.core_system["passive_effect"] += "<br>"+line.strip()
        # Active name is on the line preceded by "Active (1 CP)"
        self.core_system["active_name"] = core_lines[act_name]
        # Line after the active name is the tags for the active effect
        self.parse_tags(core_lines[act_name+1])
        # Line after the tags is the active effect
        act_effect = core_lines[act_name+2:]
        for line in act_effect:
            if self.core_system["active_effect"] == "":
                self.core_system["active_effect"] = line.strip()
            else:
                self.core_system["active_effect"] += "<br>"+line.strip()

    def parse_tags(self, tagline):
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
