# NECESSARY PREP-WORK:
# Separate pieces of gear with empty lines.
# The weapon descriptions for A/C and signature weapons modified slightly to put
#  each description on its own line.


class PilotGear:
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

    """Class for pilot gear data"""
    def __init__(self, raw_weapon=None, raw_armor=None, raw_gear=None):
        self.id = ""
        self.type = ""
        self.name = ""
        self.description = ""

        if raw_weapon:
            self.tags = []
            self.range = []
            self.damage = []
            self.parse_weapon(raw_weapon)
        elif raw_armor:
            self.parse_weapon(raw_weapon)
        elif raw_gear:
            self.parse_weapon(raw_weapon)

    def parse_weapon(self, raw_text, w_threat=False, w_range=False):
        self.type = PilotGear.TYPE_WEAPON
        # Parse name on first line.
        self.name = raw_text[0].strip()
        self.id = "pg_"+self.name.lower().replace(" ", "_")

        # Parse tags on second line.
        tags = raw_text[1].split(",")
        for t in tags:
            if t != "-\n":
                t_text = "tg_"+(t.strip().lower())
                self.tags.append({"id": t_text})

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
        r_type.strip()
        if len(tokens) > 1:
            r_val = tokens[1].strip()
        else:
            r_val = str(raw_text[2].strip())
        self.range.append(dict([("type", r_type),
                                ("val", r_val)]))

        # Parse damage on fourth line.
        self.damage = []
        damage_types = raw_text[3].split(",")
        for d in damage_types:
            tokens = d.split(" ")
            self.damage.append(dict([("type", tokens[1].strip()),
                                     ("val", tokens[0].strip())]))

        # Debugging printout
        print("\n\n============== PILOT WEAPON ====================")
        print(f"id: {self.id}")
        print(f"type: {self.type}")
        print(f"name: {self.name}")
        print(f"desc: {self.description}")
        print(f"tags: ")
        for t in self.tags:
            print(f"  {t}")
        print(f"range: ")
        for r in self.range:
            print(f"  {r}")
        print(f"damage: ")
        for d in self.damage:
            print(f"  {d}")

    def parse_armor(self, raw_text):
        self.type = PilotGear.TYPE_ARMOR

    def parse_gear(self, raw_text):
        self.type = PilotGear.TYPE_GEAR

    def set_id(self, new_id):
        self.id = new_id

    def set_name(self, new_name):
        self.name = new_name

    def set_desc(self, new_desc):
        self.description = new_desc

    def to_dict(self):
        d = {"id": self.id,
             "name": self.name,
             "type": self.type,
             "description": self.description}
        if self.type == PilotGear.TYPE_WEAPON:
            d["tags"] = self.tags
            d["range"] = self.range
            d["damage"] = self.damage
        return d