# NECESSARY PREP-WORK:
# Make sure that each talent is preceded by ONE empty line.

class PilotGear:
    START = ["PILOT GEAR\n",
             "On missions, pilots can take one set",
             "The names and descriptions given for pilot gear"]
    END = ["WILDERNESS SURVIVAL KIT",
           "Gear",
           "Contains many essentials for surviving in hostile environments:"]

    WEAPONS = "Archaic melee\n"
    ARMOR = "Light Hardsuit\n"
    GEAR = "CORRECTIVE\n"

    TYPE_WEAPON = "weapon"
    TYPE_ARMOR = "armor"
    TYPE_GEAR = "gear"

    """Class for talent data"""
    def __init__(self, raw_weapon=None, raw_armor=None, raw_gear=None):
        self.id = ""
        self.type = ""
        self.name = ""
        self.description = ""
        self.tags = []

        if raw_weapon:
            self.range = []
            self.damage = []
            self.parse_weapon(raw_weapon)
        elif raw_armor:
            self.parse_weapon(raw_weapon)
        elif raw_gear:
            self.parse_weapon(raw_weapon)

    def parse_weapon(self, raw_text, w_threat=False, w_range=False):
        self.type = PilotGear.TYPE_WEAPON
        self.name = raw_text[0].strip()
        self.id = "pg_"+self.name.lower().replace(" ", "_")
        tags = raw_text[1].split(",")
        for t in tags:
            self.tags.append(dict(["id", "tg_"+t]))
        self.range = []
        if not w_threat and not w_range:
            tokens = raw_text[2].split(" ")
            if tokens[0] == "Threat":
                w_threat = True
            elif tokens[1] == "Range":
                w_range = True
            else:
                print("Problem parsing weapon - no threat or range found!")
                print(f"  Name: {self.name}")
                print(f"  Range line: {raw_text[2]}")
        if w_threat:
            self.range.append(dict([("type", "Threat"), ("val", str(raw_text[2]))]))
        if w_range:
            self.range.append(dict([("type", "Range"), ("val", str(raw_text[2]))]))
        self.damage = []
        damage_types = raw_text[3].split(",")
        for d in damage_types:
            tokens = d.split(" ")
            self.damage.append(dict([("type", tokens[0]), ("val", tokens[0])]))

        # Debugging printout
        print("\n\n============== PILOT WEAPON ====================")
        print(f"id: {self.id}")
        print(f"type: {self.type}")
        print(f"name: {self.name}")
        print(f"desc: {self.description}\n")
        for r in self.range:
            print(f"  {r}")
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

    def set_rank(self, idx, rank_name, rank_desc):
        self.ranks[idx]["name"] = rank_name
        self.ranks[idx]["description"] = rank_desc

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "ranks": self.ranks}