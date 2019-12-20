

class PilotGear:
    """
    Class for pilot gear data.
    NECESSARY PREP-WORK:
    * Separate pieces of gear with empty lines.
    * The weapon descriptions for A/C and signature weapons modified slightly to put
    each description on its own line.
    * Change tags on hardsuits to PERSONAL ARMOR (should get fixed in later release)
    """

    START = ["PILOT GEAR\n",
             "On missions, pilots can take one set",
             "The names and descriptions given for pilot gear"]
    END = ["WILDERNESS SURVIVAL KIT",
           "Gear",
           "Contains many essentials for surviving in hostile environments:"]

    WEAPONS_SEC = "Archaic melee\n"
    ARMOR_SEC = "Light Hardsuit\n"
    GEAR_SEC = "CORRECTIVE\n"

    TYPE_WEAPON = "weapon"
    TYPE_ARMOR = "armor"
    TYPE_GEAR = "gear"

    def __init__(self, raw_weapon=None, raw_armor=None, raw_gear=None):
        """
        Initializer for Pilot Gear. Can either create a blank instance,
        or initialize a weapon, armor, or gear.
        @param raw_weapon: 3-tuple for weapon of raw text,
        threat flag, range flag (str, bool, bool).
        @param raw_armor: raw text for armor.
        @param raw_gear: raw text for gear.
        """
        self.id = ""
        self.type = ""
        self.name = ""
        self.description = ""
        self.tags = []

        if raw_weapon is not None:
            self.range = []
            self.damage = []
            self.effect = ""
            self.parse_weapon(raw_weapon[0], raw_weapon[1], raw_weapon[2])
        elif raw_armor is not None:
            self.speed = 0
            self.armor = 0
            self.edef = 10
            self.evasion = 10
            self.hp_bonus = 0
            self.parse_armor(raw_armor)
        elif raw_gear is not None:
            self.uses = 0
            self.parse_gear(raw_gear)

    def parse_weapon(self, raw_text, w_threat=False, w_range=False):
        """
        Parses raw weapon text into the object.
        @param raw_text: Raw text, stored as a list of strings.
        @param w_threat: Flag for whether the weapon was in a table with a
        Threat column.
        @param w_range: Flag for whether the weapon was in a table with a
        Range column.
        @return: None
        """
        self.type = PilotGear.TYPE_WEAPON
        # Parse name and id from first line.
        self.name = raw_text[0].strip().title()
        self.id = "pg_"+self.name.lower().replace(" ", "_").replace("/", "")

        # Parse tags on second line.
        self.parse_tags(raw_text[1])

        # Parse range on third line.
        self.range = []
        # If threat/range wasn't specified, look for it.
        tokens = raw_text[2].split(" ")
        if not w_threat and not w_range:
            if tokens[0].strip() == "Threat":
                w_threat = True
            elif tokens[0].strip() == "Range":
                w_range = True
            else:
                print("Problem parsing weapon - no threat or range found!")
                print(f"  Name: {self.name}")
                print(f"  Range line: {raw_text[2]}")
        # Set string for threat/range
        r_type = ""
        if w_threat:
            r_type += " Threat"
        if w_range:
            r_type += " Range"
        r_type = r_type.strip()
        if len(tokens) > 1:
            r_val = int(tokens[1].strip())
        else:
            r_val = int(raw_text[2].strip())
        self.range.append(dict([("type", r_type),
                                ("val", r_val)]))

        # Parse damage on fourth line.
        self.damage = []
        damage_types = raw_text[3].split(",")
        for d in damage_types:
            tokens = d.split(" ")
            if "*" in tokens[1]:
                d_type = "variable"
                self.effect = "Player selects damage type at item creation."
            else:
                d_type = tokens[1].strip()
            d_val = int(tokens[0])
            self.damage.append(dict([("type", d_type),
                                     ("val", d_val)]))

        # Debugging printout
        # print("\n\n============== PILOT WEAPON ====================")
        # print(f"id: {self.id}")
        # print(f"type: {self.type}")
        # print(f"name: {self.name}")
        # print(f"desc: {self.description}")
        # print(f"tags: ")
        # for t in self.tags:
        #     print(f"  {t}")
        # print(f"range: ")
        # for r in self.range:
        #     print(f"  {r}")
        # print(f"damage: ")
        # for d in self.damage:
        #     print(f"  {d}")

    def parse_armor(self, raw_text):
        """
        Parses raw armor text into the object.
        @param raw_text: Raw text as a list of strings
        @return: None
        """
        self.type = PilotGear.TYPE_ARMOR
        # Parse name and id from first line.
        self.name = raw_text[0].strip()
        self.id = "pg_"+self.name.lower().replace(" ", "_").replace("/", "")

        # Parse tags on 2nd line
        self.parse_tags(raw_text[1])

        # Parse hp bonus on 3rd line
        if raw_text[2].startswith("+"):
            bonus = raw_text[2].split(" ")[0].replace("+", "")
            self.hp_bonus = int(bonus)

        # Parse armor on 4th line
        self.armor = int(raw_text[3])
        # Parse Evasion on 5th line
        self.evasion = int(raw_text[4])
        # Parse E-Defense on 6th line
        self.edef = int(raw_text[5])
        # Parse Speed on 7th line
        self.speed = int(raw_text[6])

        # Debugging printout
        # print("\n\n============== PILOT ARMOR ====================")
        # print(f"id: {self.id}")
        # print(f"type: {self.type}")
        # print(f"name: {self.name}")
        # print(f"desc: {self.description}")
        # print(f"tags: ")
        # for t in self.tags:
        #     print(f"  {t}")
        # print(f"hp_bonus: {self.hp_bonus}")
        # print(f"armor: {self.armor}")
        # print(f"evasion: {self.evasion}")
        # print(f"edef: {self.edef}")
        # print(f"speed: {self.speed}")

    def parse_gear(self, raw_text):
        """
        Parses raw gear text into the object
        @param raw_text: Raw text as a list of strings
        @return: None
        """
        self.type = PilotGear.TYPE_GEAR
        # Parse name and id from first line.
        self.name = raw_text[0].strip()
        self.id = "pg_"+self.name.lower().replace(" ", "_").replace("/", "")

        # Parse tags from second line.
        self.parse_tags(raw_text[1])

        # Combine remaining lines to create the description.
        self.description = raw_text[2].strip()
        if len(raw_text) > 3:
            for line in raw_text[3:]:
                self.description += "<br>"+line.strip()

    def set_id(self, new_id):
        self.id = new_id

    def set_name(self, new_name):
        self.name = new_name

    def set_desc(self, new_desc):
        self.description = new_desc

    def parse_tags(self, tagline):
        tags = tagline.split(",")
        for t in tags:
            if t != "-\n":
                words = t.strip().split(" ")
                # Add "uses" field if gear has limited uses.
                if words[0] == "Limited":
                    self.uses = int(words[-1])
                # If we want no Limited tags on pilot gear, change the line below
                #   to an elif.
                if words[-1].isdecimal():
                    t_text = ""
                    for w in words[:-1]:
                        t_text += " "+w
                    d = {"id": "tg_"+(t_text.strip().lower().replace(" ", "_")),
                         "val": int(words[-1])}
                else:
                    d = {"id": "tg_"+(t.strip().lower().replace(" ", "_"))}
                self.tags.append(d)

    def to_dict(self):
        d = {"id": self.id,
             "name": self.name,
             "type": self.type,
             "description": self.description,
             "tags": self.tags}
        if self.type == PilotGear.TYPE_WEAPON:
            d["range"] = self.range
            d["damage"] = self.damage
            if self.effect != "":
                d["effect"] = self.effect
        elif self.type == PilotGear.TYPE_ARMOR:
            d["hp_bonus"] = self.hp_bonus
            d["armor"] = self.armor
            d["evasion"] = self.evasion
            d["edef"] = self.edef
            d["speed"] = self.speed
        elif self.type == PilotGear.TYPE_GEAR:
            if self.uses > 0:
                d["uses"] = self.uses
        return d