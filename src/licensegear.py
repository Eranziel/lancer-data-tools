# /bin/python3
# -*- utf-8 -*-

from parseutil import *


class IMechGear:
    """
    Interface for mech gear, defining common methods.
    """

    def parse_tags(self, tagline):
        """
        Parse tags for mech gear.
        @param tagline: str: The line of text which contains the tags.
        @return: None.
        """
        if "SP" in tagline:
            self.sp = int(tagline.split(",")[0].split(" ")[0])
            # Take the "X SP," substring off of the front.
            tagline = tagline.partition(",")[2]

        tags = tagline.split(",")
        for t in tags:
            if t != "-":
                if "/" in t:
                    num, slash, t_text = t.strip().partition("/")
                    # If there is a number before the slash, parse it as 'val'.
                    val = None
                    if num.isdecimal():
                        val = int(num)
                    # If it wasn't a number, parse the whole text as a regular tag.
                    else:
                        t_text = t
                else:
                    words = t.strip().split(" ")
                    # If the tag contains a number, parse it as 'val'.
                    val = None
                    t_text = ""
                    for word in words:
                        if word.isdecimal():
                            val = int(word)
                        elif is_die_roll(word):
                            val = word
                        else:
                            t_text += " "+word
                t_text.strip()
                d = {"id": gen_id("tg_", t_text)}
                if val is not None:
                    d["val"] = val
                # Don't add non-existent tags
                if d["id"] != "tg_" and not is_duplicate_tag(d, self.tags):
                    self.tags.append(d)

    def set_level(self, lic_table):
        """
        Set the license and level for the piece of gear.
        @param lic_table: [[str]]: 1st index is the license level, 2nd index is the
        name of the gear/frame that unlocks at that level.
        @return: None.
        """
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
    * Each weapon must be preceded and followed by an empty line.
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

    def parse_text(self, raw, src):
        """
        Parse the raw text for the weapon mod.
        @param raw: [str]: The text to parse.
        @param src: str: The source manufacturer.
        @return: None.
        """
        self.source = src
        self.name = raw[0].strip().upper()
        self.id = gen_id(Mod.PREFIX, self.name)

        self.parse_tags(raw[1].strip())

        # Find effect/description split
        splits = []
        for i in range(len(raw)):
            if raw[i] == "---\n":
                splits.append(i)

        raw_effect = []
        raw_desc = []
        # Effects are from tag line to description
        if len(splits) > 0:
            raw_effect += raw[2:splits[0]]
        # No splits - everything after tags is effects
        else:
            raw_effect += raw[2:]
        # More than one split
        if len(splits) > 1:
            # Description is between the two splits
            raw_desc += raw[splits[0] + 1:splits[1]]
            # Add everything after 2nd split to the effect
            raw_effect += raw[splits[1] + 1:]
        # 1 split, description follows effect
        elif len(splits) > 0:
            raw_desc += raw[splits[0] + 1:]

        self.description = combine_lines(raw_desc, check_horus=self.source == "HORUS")
        self.effect = combine_lines(raw_effect)

        self.parse_applied()

    def parse_applied(self):
        """
        Check the effect line for the weapons this mod can apply to.
        @return: None.
        """
        applied_list = self.effect[:self.effect.find(":")]

        # Find all the weapon types mentioned in the mod's effect.
        for word in applied_list.strip().replace(",", "").split(" "):
            if word.upper() in Weapon.TYPES:
                self.applied_to.append(word.strip().lower())

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
            self.applied_to = [item.lower() for item in Weapon.TYPES]
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
    * Gorgon license table missing hyphen in "SCYLLA-Class NHP".
    """

    GMS_SYSTEMS = "GMS General Market Systems\n"
    GMS_FLIGHT = "GMS Flight Systems\n"
    GMS_SYS_END = "You can fly when you Boost or make a standard move;"

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

    def parse_text(self, raw, src):
        """
        Parse the text for the mech system.
        @param raw: [str]: The raw text.
        @param src: str: The source manufacturer.
        @return: None.
        """
        self.source = src
        self.name = raw[0].strip().upper()
        self.id = gen_id(System.PREFIX, self.name)

        self.parse_tags(raw[1].strip())

        # Find effect/description split
        splits = []
        for i in range(len(raw)):
            if raw[i] == "---\n":
                splits.append(i)

        raw_effect = []
        raw_desc = []
        # Effects are from tag line to description
        if len(splits) > 0:
            raw_effect += raw[2:splits[0]]
        # No splits - everything after tags is effects
        else:
            raw_effect += raw[2:]
        # More than one split
        if len(splits) > 1:
            # Description is between the two splits
            raw_desc += raw[splits[0] + 1:splits[1]]
            # Add everything after 2nd split to the effect
            raw_effect += raw[splits[1] + 1:]
        # 1 split, description follows effect
        elif len(splits) > 0:
            raw_desc += raw[splits[0] + 1:]

        self.description = combine_lines(raw_desc, check_horus=(src == "HORUS"))
        self.effect = combine_lines(raw_effect)
        # Inherit tags from the effect action, if any.
        if "mech gains the AI" in raw_effect[0]:
            for line in raw_effect:
                if line.startswith("- "):
                    check_line = line.replace("- ", "", 1).strip()
                else:
                    check_line = line.strip()
                if (check_line.startswith("Protocol") or
                        check_line.endswith(", Protocol") or
                        check_line.startswith("Quick Action") or
                        check_line.startswith("Full Action") or
                        check_line.startswith("Quick Tech") or
                        check_line.startswith("Full Tech") or
                        check_line.startswith("Reaction")):
                    self.parse_tags(check_line)

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
        if ("Deployable" in self.effect
                or ("(Mine" in self.effect and "(Grenade" in self.effect)):
            self.type = "Deployable"
        elif ("Drone" in self.effect):
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
    * Ensure each damage stat has "damage" inside the square brackets.
    * Each damage stat with multiple types must have each type separated by " + ".
    * HMG typo: 1d6+4 damage should be 2d6+4.
    * Nanocarbon Sword: add spaces between numbers and threat/damage.
    * Gavity Gun: fix blast and damage stats.
    * Displacer: separate range and blast into their own brackets.
    """

    PREFIX = "mw_"

    GMS_WEP_TABLE = "GMS Mech Weapons\n"
    GMS_WEP_END = "GMS General Market Systems\n"
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
    RANGE = ["range", "threat", "burst", "blast", "cone", "line"]
    DAMAGE = ["damage", "heat", "burn"]

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
        """
        Parse the raw text for the weapon.
        @param raw: [str]: The text to parse.
        @param gms: [str] or None: List of GMS weapon descriptions.
        @param src: str: Source manufacturer.
        @return: None.
        """
        self.source = src
        self.name = raw[0].strip().upper()
        self.id = gen_id(Weapon.PREFIX, self.name)

        if gms is not None:
            w_type, d, tags = raw[1].strip().partition(",")
            self.parse_type(w_type)
            self.parse_tags(tags)
            self.parse_stats(raw[2])
            # Parse second stat line if it's present.
            if len(raw) > 3:
                self.parse_stats(raw[3])
            for i in range(len(Weapon.GMS_TYPE_LIST)):
                gms_type = Weapon.GMS_TYPE_LIST[i]
                if self.name.lower() in gms_type:
                    self.description = gms[i]
        else:
            # Parse the mount, type, and tags on second line
            if "," in raw[1]:
                tag_line = raw[1].strip()
                if "SP" in tag_line:
                    tokens = tag_line.split(", ")
                    # Find and parse the SP
                    for t in tokens:
                        if "SP" in t:
                            self.parse_tags(t)
                            tokens.remove(t)
                            break
                    tag_line = ""
                    # Reconstruct the line without SP
                    for t in tokens:
                        if tag_line == "":
                            tag_line = t
                        else:
                            tag_line += ", " + t
                type_line, d, tags = tag_line.strip().partition(", ")
                self.parse_type(type_line)
                self.parse_tags(tags)
            else:
                self.parse_type(raw[1].strip())

            # Stats are on 3rd line
            self.parse_stats(raw[2].strip())

            # Find effect/description split
            splits = []
            for i in range(len(raw)):
                if raw[i] == "---\n":
                    splits.append(i)

            raw_effect = []
            raw_desc = []
            # Effects are from spec line to description
            if len(splits) > 0:
                raw_effect += raw[3:splits[0]]
            # No splits - everything after stats is description
            else:
                raw_desc += raw[3:]
            # More than one split
            if len(splits) > 1:
                # Description is between the two splits
                raw_desc += raw[splits[0]+1:splits[1]]
                # Add everything after 2nd split to the effect
                raw_effect += raw[splits[1]+1:]
            # 1 split, description follows effect
            elif len(splits) > 0:
                raw_desc += raw[splits[0]+1:]

            self.description = combine_lines(raw_desc, check_horus=True)
            self.effect = combine_lines(raw_effect)

    def parse_type(self, type_line):
        """
        Parse the weapon size and type.
        @param type_line: str: Text for the size and type.
        @return: None.
        """
        words = type_line.split(" ")
        self.mount = words[0].strip()
        self.type = words[1].strip()

    def parse_stats(self, line):
        """
        Parse the range and damage spec line.
        @param line: str: The line with range and damage.
        @param gms: bool: If True, use GMS table parsing.
        @return: None.
        """
        parts = line.strip().split("]")
        if "" in parts:
            parts.remove("")
        for part in parts:
            # Remove the other square bracket
            part = part.replace("[", "").strip()
            words = part.split(" ")

            # Mimic gun special case
            if "???" in words:
                if "range" in words:
                    d = dict([
                        ("override", True),
                        ("type", "Range"),
                        ("val", "???")
                    ])
                    self.range.append(d)
                elif "damage" in words:
                    d = dict([
                        ("override", True),
                        ("val", "??? kinetic")
                    ])
                    self.damage.append(d)
            # Parse range stat
            elif words[0] in Weapon.RANGE:
                if " or " in part:
                    parts.append(part[part.rfind(" or ")+4:])

                r_type = words[0].strip().title()
                val = words[1].strip()
                if val.isdecimal():
                    val = int(val)
                d = dict([
                    ("type", r_type),
                    ("val", val)
                ])
                self.range.append(d)
            else:
                # Check whether this part is a damage stat
                dmg = False
                for harm in Weapon.DAMAGE:
                    if harm in part:
                        dmg = True
                        break
                # Parse damage stat
                if dmg:
                    d_type = ""
                    val = ""
                    # If the damage stat has "or" in it, it's variable
                    if " or " in part:
                        d_type = "variable"
                    for word in words:
                        word = word.strip()

                        if word.isdecimal():
                            val = int(word)
                        elif is_die_roll(word):
                            val = word
                        elif word[0].isdecimal() and word[-1].isdecimal():
                            val = word
                        elif word != "damage" and word != "+":
                            d_type = word

                        if val != "" and d_type != "":
                            d = dict([
                                ("type", d_type),
                                ("val", val)
                            ])
                            self.damage.append(d)
                            d_type = val = ""

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
