from parseutil import *


class IMechGear:
    """
    Interface for mech gear, defining common methods.
    """
    def parse_tags(self, tagline):
        if "SP" in tagline:
            self.sp = int(tagline.split(",")[0].split(" ")[0])
            # Take the "X SP," substring off of the front.
            tagline = tagline.partition(",")[2]

        tags = tagline.split(",")
        for t in tags:
            if t != "-\n":
                words = t.strip().split(" ")
                # If the tag contains a number, parse it as 'val'.
                val = None
                t_text = ""
                for word in words:
                    if word.isdecimal():
                        val = int(word)
                    else:
                        t_text += " "+word
                t_text.strip()
                d = {"id": gen_id("tg_", t_text)}
                if val is not None:
                    d["val"] = val
                self.tags.append(d)

    def set_level(self, lic_table):
        for i in range(len(lic_table)):
            for item in lic_table[i]:
                if " frame" in item:
                    self.license = item[:item.find(" frame")].upper()
                if self.name.lower() == item.lower():
                    self.license_level = i+1
        if self.license_level == "":
            print(f"Problem setting level for {self.name}")
            for line in lic_table:
                print(f"    {line}")


class Mod(IMechGear):
    """
    Class for weapon mods.
    NECESSARY PREP WORK:
    *
    """
    def __init__(self, raw_text=None):
        pass


class System(IMechGear):
    """
    Class for mech systems.
    NECESSARY PREP WORK:
    * Each system must be preceded and followed by an empty line.
    * Add a line containing "---" between the description and effect of each system.
      Systems which do not have this line are assumed to not have a description.
    """

    GMS_SYSTEMS = "GMS GENERAL MARKET SYSTEMS\n"
    GMS_FLIGHT = "GMS FLIGHT SYSTEMS\n"
    GMS_SYS_END = "You can fly when you BOOST or make a standard move; however"

    def __init__(self, raw=None, src=None):
        """
        Create a new system.
        @param raw: [str]: raw text.
        @param src: str: source manufacturer.
        """
        self.id = ""
        self.name = ""
        self.type = "System"
        self.sp = 0
        self.tags = []
        self.source = ""
        self.license = ""
        self.license_level = ""
        self.effect = ""
        self.description = ""
        self.data_type = "system"
        self.aptitude = dict([])

        if raw is not None:
            self.source = src
            self.parse_text(raw)

    def __str__(self):
        output = "\n\n============== SYSTEM ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\ntype: {self.type}"
        output += f"\nsp: {self.sp}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        output += f"\nsource: {self.source}"
        output += f"\nlicense: {self.license}"
        output += f"\nll: {self.license_level}"
        output += f"\ndesc: {self.description}"
        output += f"\neffect: {self.effect}"
        output += f"\ndata_type: {self.data_type}"
        output += f"\naptitude: {self.aptitude}"
        return output

    def parse_text(self, raw_text):
        self.name = raw_text[0].strip()
        self.id = gen_id("ms_", self.name)

        self.parse_tags(raw_text[1])

        # Find the split between description and effect
        split = -1
        for i in range(len(raw_text)):
            if raw_text[i] == "---\n":
                split = i
                break
        if split > 0:
            for line in raw_text[2:split]:
                if self.description == "":
                    self.description = line.strip()
                else:
                    self.description += "<br>"+line.strip()
            for line in raw_text[split+1:]:
                if self.effect == "":
                    self.effect = line.strip()
                else:
                    self.effect += "<br>"+line.strip()
        else:  # No split means there is no description.
            for line in raw_text[2:]:
                if self.effect == "":
                    self.effect = line.strip()
                else:
                    self.effect += "<br>"+line.strip()

        # Set system type based on tags
        for tag in self.tags:
            if tag["id"] == "tg_ai":
                self.type = "AI"
                break
            elif tag["id"] == "tg_drone":
                self.type = "Drone"
                break
            elif tag["id"] == "tg_deployable":
                self.type = "Deployable"
                break
            elif tag["id"] == "tg_shield":
                self.type = "Shield"
                break
        # Set system type based on effect
        if ("DEPLOYABLE" in self.effect
                or ("(Mine" in self.effect and "(Grenade" in self.effect)):
            self.type = "Deployable"
        elif ("DRONE" in self.effect):
            self.type = "Drone"

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "type": self.type,
                "sp": self.sp,
                "tags": self.tags,
                "source": self.source,
                "license": self.license,
                "license_level": self.license_level,
                "effect": self.effect,
                "description": self.description,
                "data_type": self.data_type,
                "aptitude": self.aptitude}


class Weapon(IMechGear):
    """
    Class for mech weapons.
    NECESSARY PREP WORK:
    * Each weapon must be preceded and followed by an empty line.
    """

    GMS_WEP_TABLE = "GMS MECH WEAPONS\n"
    GMS_WEP_END = "GMS GENERAL MARKET SYSTEMS\n"
    TYPES = ["Melee", "CQB", "Rifle", "Launcher", "Cannon", "Nexus", "???"]
    MOUNTS = ["Auxiliary", "Main", "Heavy", "Superheavy"]
    RANGE = "R: "
    THREAT = "T: "
    DAMAGE = "D: "
    RANGES = dict([
        ("Range", "Range"),
        ("R:", "Range"),
        ("Threat", "Threat"),
        ("T:", "Threat"),
        ("Blast", "Blast"),
        ("Bust", "Bust"),
        ("Line", "Line"),
        ("Cone", "Cone")
    ])
    DAM_TYPES = ["kinetic", "explosive", "energy", "burn", "heat", "variable"]

    def __init__(self, raw_text=None, gms=None, src="", lic_table=[]):
        self.id = ""
        self.name = ""
        self.mount = ""
        self.type = ""
        self.damage = []
        self.range = []
        self.tags = []
        self.source = ""
        self.license = ""
        self.license_level = ""
        self.effect = ""
        self.description = ""
        self.data_type = "weapon"
        self.aptitude = dict([])

        if raw_text is not None:
            self.parse_text(raw_text, gms, src)
        if len(lic_table) > 0:
            self.set_level(lic_table)

    def __str__(self):
        output = "\n\n============== WEAPON ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\nmount: {self.mount}"
        output += f"\ntype: {self.type}"
        if hasattr(self, 'sp'):
            output += f"\nsp: {self.sp}"
        output += f"\ndamage:"
        for d in self.damage:
            output += f"\n   {d}"
        output += f"\nrange:"
        for r in self.range:
            output += f"\n   {r}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        output += f"\nsource: {self.source}"
        output += f"\nlicense: {self.license}"
        output += f"\nll: {self.license_level}"
        output += f"\ndesc: {self.description}"
        output += f"\neffect: {self.effect}"
        output += f"\ndata_type: {self.data_type}"
        output += f"\naptitude: {self.aptitude}"
        return output

    def parse_text(self, raw, gms, src):
        self.source = src
        self.name = raw[0].strip()
        self.id = gen_id("mw_", self.name)

        if gms is not None:
            self.parse_type(raw[1])
            self.parse_tags(raw[2])
            self.parse_stats(raw[3], gms=True)
            self.parse_damage(raw[4])
            self.description = gms
        else:
            # Parse the mount, type, and tags on second line
            if "," in raw[1]:
                type_line, d, tags = raw[1].strip().partition(", ")
                self.parse_type(type_line)
                self.parse_tags(tags)
            else:
                self.parse_type(raw[1].strip())

            # Find the spec line
            spec_line = 0
            for i in range(len(raw)):
                if raw[i].startswith(Weapon.RANGE) or \
                        raw[i].startswith(Weapon.THREAT):
                    spec_line = i
                    break
            self.parse_stats(raw[spec_line])
            # Description is from 3rd line until spec line
            for line in raw[2:spec_line]:
                if self.description == "":
                    self.description = line.strip()
                else:
                    self.description += line.strip()
            # Effects are everything after spec line
            for line in raw[spec_line+1:]:
                if self.effect == "":
                    self.effect = line.strip()
                else:
                    self.effect += line.strip()

    def parse_type(self, type_line):
        words = type_line.split(" ")
        self.mount = words[0].strip()
        self.type = words[1].strip()

    def parse_stats(self, line, gms=False):
        if gms:
            line = line.strip()
            if "/" in line:
                ranges = line.split("/")
            else:
                ranges = [line]
            for r in ranges:
                # If the range spec is only a number, it is range
                if r.isnumeric():
                    d = dict([
                        ("type", Weapon.RANGES["Range"]),
                        ("val", int(r))
                    ])
                    self.range.append(d)
                else:
                    words = r.split(" ")
                    d = dict([
                        ("type", words[0]),
                        ("val", int(words[1]))
                    ])
                    self.range.append(d)
        else:
            parts = line.strip().split("\t")
            for part in parts:
                # Parse range spec
                if part.startswith(Weapon.RANGE):
                    part = part.replace(Weapon.RANGE, "")
                    if "," in part:
                        subs = part.split(",")
                    elif " or " in part:
                        subs = part.partition(" or ")
                        subs = [subs[0], subs[2]]
                    else:
                        subs = [part]
                    for r in subs:
                        r = r.strip()
                        if r.isnumeric():
                            d = dict([
                                ("type", Weapon.RANGES["Range"]),
                                ("val", int(r))
                            ])
                            self.range.append(d)
                        else:
                            words = r.split(" ")
                            if "???" in words:
                                d = dict([
                                    ("override", True),
                                    ("type", Weapon.RANGES["Range"]),
                                    ("val", "???")
                                ])
                            else:
                                d = dict([
                                    ("type", words[0].strip().title()),
                                    ("val", int(words[1].strip()))
                                ])
                            self.range.append(d)
                # Parse threat spec
                elif part.startswith(Weapon.THREAT):
                    part = part.replace(Weapon.THREAT, "")
                    if part.isnumeric():
                        d = dict([
                            ("type", Weapon.RANGES["Threat"]),
                            ("val", int(part))
                        ])
                        self.range.append(d)
                # Parse damage spec
                elif part.startswith(Weapon.DAMAGE):
                    self.parse_damage(part.replace(Weapon.DAMAGE, ""))

    def parse_damage(self, dam_str):
        dam_str = dam_str.strip()
        delim = " + "
        types = []
        if delim in dam_str:
            sub = dam_str
            while delim in sub:
                parts = sub.partition(delim)
                types.append(parts[0])
                sub = parts[2]
            types.append(sub)
        else:
            types.append(dam_str)

        for t in types:
            tokens = t.split(" ")
            # Damage amount of "???" is special
            if tokens[0] == "???":
                dam = dict([
                    ("override", True),
                    ("val", "??? kinetic")
                ])
            elif tokens[0] == "Special":
                dam = dict([
                    ("override", True),
                    ("val", "special")
                ])
            else:
                dam = dict([
                    ("type", tokens[1]),
                    ("val", tokens[0])
                ])
            self.damage.append(dam)

    def to_dict(self):
        d = dict([
            ("id", self.id),
            ("name", self.name),
            ("mount", self.mount),
            ("type", self.type),
            ("damage", self.damage),
            ("range", self.range),
            ("tags", self.tags),
            ("source", self.source),
            ("license", self.license),
            ("license_level", self.license_level),
            ("effect", self.effect),
            ("description", self.description),
            ("data_type", self.data_type),
            ("aptitude", self.aptitude),
        ])
        if hasattr(self, "sp"):
            d["sp"] = self.sp
        return d
