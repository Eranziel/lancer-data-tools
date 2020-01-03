

class CoreBonus:

    CORE = "CORE BONUSES\n"
    GMS = "GENERAL MASSIVE SYSTEMS\n"
    IPSN = "IPS-NORTHSTAR\n"
    SSC = "SMITH-SHIMANO CORPRO\n"
    HORUS = "HORUS\n"
    HA = "HARRISON ARMORY\n"

    def __init__(self, raw=None):
        self.id = ""
        self.name = ""
        self.source = ""
        self.effect = ""
        self.description = ""

        if raw is not None:
            self.parse_text(raw)

    def parse_text(self, raw):
        self.source = raw[0].strip()
        text = raw[1]

        self.name = text[0].strip()
        self.id = "cb_" + self.name.lower().replace(" ", "_").replace("-", "_").replace("'", "")
        self.description = text[1].strip()
        self.effect = text[2].strip()

        # Debugging printout
        print("\n\n============== CORE BONUS ====================")
        print(f"id: {self.id}")
        print(f"name: {self.name}")
        print(f"source: {self.source}")
        print(f"effect: {self.effect}")
        print(f"desc: {self.description}")

    def to_dict(self):
        return dict([
            ("id", self.id),
            ("name", self.name),
            ("source", self.source),
            ("effect", self.effect),
            ("description", self.description)
        ])
