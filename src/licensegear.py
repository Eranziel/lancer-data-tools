# /bin/python3
# -*- utf-8 -*-

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
        # print(f"tag line: {tags}")
        for t in tags:
            if t != "-":
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
                # Don't add non-existent tags
                if d["id"] != "tg_":
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

    PREFIX = "wm_"

    def __init__(self, raw_text=None, src="", lic_table=[]):
        """
        Create a new weapon mod.
        @param raw_text: [str]: raw text.
        @param src: str: source manufacturer.
        """
        self.id = ""
        self.name = ""
        self.sp = 0
        self.tags = []
        self.applied_to = []
        self.applied_string = ""
        self.source = ""
        self.license = ""
        self.license_level = 0
        self.effect = ""
        self.description = ""
        self.data_type = "mod"
        self.added_tags = []
        self.added_range = dict([])
        self.added_damage = dict([])
        self.aptitude = dict([])

        if raw_text is not None:
            self.parse_text(raw_text, src)
        if len(lic_table) > 0:
            self.set_level(lic_table)

    def __str__(self):
        output = "\n\n============== MOD ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\nsp: {self.sp}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        output += f"\napplied_to:"
        for apply in self.applied_to:
            output += f"\n   {apply}"
        output += f"\napplied_string: {self.applied_string}"
        output += f"\nsource: {self.source}"
        output += f"\nlicense: {self.license}"
        output += f"\nll: {self.license_level}"
        output += f"\ndesc: {self.description}"
        output += f"\neffect: {self.effect}"
        output += f"\ndata_type: {self.data_type}"
        return output

    def parse_text(self, raw_text, src):
        self.source = src
        self.name = raw_text[0].strip()
        self.id = gen_id(Mod.PREFIX, self.name)

        self.parse_tags(raw_text[1].strip())

        # Find the split between description and effect
        split = -1
        for i in range(len(raw_text)):
            if raw_text[i] == "---\n":
                split = i
                break
        if split > 0:
            # Description
            for line in raw_text[2:split]:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
                if self.description == "":
                    self.description = line.strip()
                else:
                    self.description += "<br>"+line.strip()
            # Effect
            for line in raw_text[split+1:]:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
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

        self.parse_applied()

    def parse_applied(self):
        """
        Check the effect line for the weapons this mod can apply to.
        @return:
        """
        applied_list = self.effect[:self.effect.find(":")]

        # Find all the weapon types mentioned in the mod's effect.
        for word in applied_list.strip().replace(",", "").split(" "):
            if word in Weapon.TYPES:
                self.applied_to.append(word.strip())

        # Create the applied string - user-visible string.
        # Start by checking whether it works on all weapons.
        applies_any = True
        for w_type in Weapon.TYPES:
            applies_any = applies_any and w_type in self.applied_to
        if applies_any:
            self.applied_string = "Any"
        # It doesn't work on all weapons.
        else:
            # Next check whether it works on all ranged weapons.
            ranged_types = Weapon.TYPES.copy()
            ranged_types.remove("MELEE")
            applies_ranged = True
            for w_type in ranged_types:
                applies_ranged = applies_ranged and w_type in self.applied_to
            if applies_ranged:
                self.applied_string = "Any Ranged"
            # It doesn't apply to all ranged weapons.
            # Add all the type strings together, with commas between.
            else:
                self.applied_string = ""
                for a_t in self.applied_to:
                    # First type becomes the base string.
                    if self.applied_string == "":
                        self.applied_string = a_t
                    # Add the last weapon type, preceded by "or".
                    elif a_t == self.applied_to[-1]:
                        if len(self.applied_to) > 2:
                            self.applied_string += ", or " + a_t
                        else:
                            self.applied_string += " or " + a_t
                    # Not first and not last, just put a comma in between.
                    else:
                        self.applied_string += ", " + a_t
        # If we get to here and applied_to and applied_string are empty, it applies to all.
        if self.applied_string == "" and len(self.applied_to) == 0:
            self.applied_to = Weapon.TYPES.copy()
            self.applied_string = "Any"

    def to_dict(self):
        d = {"id": self.id,
             "name": self.name,
             "sp": self.sp,
             "applied_to": self.applied_to,
             "applied_string": self.applied_string,
             "source": self.source,
             "license": self.license,
             "license_level": self.license_level,
             "effect": self.effect,
             "description": self.description,
             "data_type": self.data_type,
             "aptitude": self.aptitude}
        if len(self.tags) > 0:
            d["tags"] = self.tags
        if len(self.added_tags) > 0:
            d["added_tags"] = self.added_tags
        if len(self.added_range) > 0:
            d["added_range"] = self.added_range
        if len(self.added_damage) > 0:
            d["added_damage"] = self.added_damage
        return d


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

    PREFIX = "ms_"

    def __init__(self, raw_text=None, src="", lic_table=()):
        """
        Create a new system.
        @param raw_text: [str]: raw text.
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

        if raw_text is not None:
            self.parse_text(raw_text, src)
        if len(lic_table) > 0:
            self.set_level(lic_table)

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

    def parse_text(self, raw_text, src):
        self.source = src
        self.name = raw_text[0].strip()
        self.id = gen_id(System.PREFIX, self.name)

        self.parse_tags(raw_text[1].strip())

        # Find the split between description and effect
        split = -1
        for i in range(len(raw_text)):
            if raw_text[i] == "---\n":
                split = i
                break
        if split > 0:
            # Description
            for line in raw_text[2:split]:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
                if line.startswith("[") and line.endswith("]"):
                    line = "<span class='ra-quiet'>"+line+"</span>"
                if self.description == "":
                    self.description = line.strip()
                else:
                    self.description += "<br>"+line.strip()
            # Effect
            raw_effect = raw_text[split+1:]
            for line in raw_effect:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
                if self.effect == "":
                    self.effect = line.strip()
                else:
                    self.effect += "<br>"+line.strip()
        else:  # No split means there is no description.
            raw_effect = raw_text[2:]
            for line in raw_effect:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
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
            elif tag["id"] == "tg_quick_tech" or tag["id"] == "tg_full_tech":
                self.type = "Tech"
                break
        # Set system type based on effect
        if ("DEPLOYABLE" in self.effect
                or ("(Mine" in self.effect and "(Grenade" in self.effect)):
            self.type = "Deployable"
        elif ("DRONE" in self.effect):
            self.type = "Drone"
        elif ("tech action" in self.effect.lower() or
              "tech attack" in self.effect.lower()):
            self.type = "Tech"

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

    PREFIX = "mw_"

    GMS_WEP_TABLE = "GMS MECH WEAPONS\n"
    GMS_WEP_END = "GMS GENERAL MARKET SYSTEMS\n"
    GMS_TYPES = ["Type-I (T-1)", "Type-II (T-2)", "Type-III (T-3)"]
    GMS_T2_THERMAL = "GMS's T-2 energy weapons,"
    GMS_TYPE_LIST = [
        ["assault rifle",
         "heavy machine gun",
         "heavy melee weapon",
         "pistol",
         "shotgun",
         "tactical knife",
         "tactical melee weapon"],
        ["charged blade",
         "heavy charged blade"],
        ["thermal lance",
         "thermal pistol",
         "thermal rifle"],
        ["anti-materiel rifle",
         "cyclone pulse rifle",
         "howitzer",
         "missile rack",
         "mortar",
         "nexus (hunter-killer)",
         "nexus (light)",
         "rocket-propelled grenade",
         "segment knife"]
    ]

    TYPES = ["MELEE", "CQB", "RIFLE", "LAUNCHER", "CANNON", "NEXUS"]
    MOUNTS = ["Auxiliary", "Main", "Heavy", "Superheavy"]
    RANGE = "R: "
    THREAT = "T: "
    DAMAGE = "D: "

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
        self.id = gen_id(Weapon.PREFIX, self.name)
        # self.id = gen_id("mw_", self.name)

        if gms is not None:
            self.parse_type(raw[1])
            self.parse_tags(raw[2].strip())
            self.parse_stats(raw[3], gms=True)
            self.parse_damage(raw[4])
            for i in range(len(Weapon.GMS_TYPE_LIST)):
                gms_type = Weapon.GMS_TYPE_LIST[i]
                if self.name.lower() in gms_type:
                    self.description = gms[i]
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
                        raw[i].startswith(Weapon.THREAT) or \
                        raw[i].startswith(Weapon.DAMAGE):
                    spec_line = i
                    break
            self.parse_stats(raw[spec_line])
            # Description is from 3rd line until spec line
            for line in raw[2:spec_line]:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
                if self.description == "":
                    self.description = line.strip()
                else:
                    self.description += line.strip()
            # Effects are everything after spec line
            for line in raw[spec_line+1:]:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
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
                        ("type", "Range"),
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
                                ("type", "Range"),
                                ("val", int(r))
                            ])
                            self.range.append(d)
                        else:
                            words = r.split(" ")
                            if "???" in words:
                                d = dict([
                                    ("override", True),
                                    ("type", "Range"),
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
                            ("type", "Threat"),
                            ("val", int(part))
                        ])
                        self.range.append(d)
                # Parse damage spec
                elif part.startswith(Weapon.DAMAGE):
                    self.parse_damage(part.replace(Weapon.DAMAGE, ""))

    def parse_damage(self, dam_str):
        dam_str = dam_str.strip().replace(".", "")
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
            # If the damage has an "or" in it, it's variable.
            if " or " in t:
                dam = dict([
                    ("type", "variable"),
                    ("val", tokens[0])
                ])
            # Damage amount of "???" is special
            elif tokens[0] == "???":
                dam = dict([
                    ("override", True),
                    ("val", "??? kinetic")
                ])
            elif tokens[0] == "Special":
                return
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
