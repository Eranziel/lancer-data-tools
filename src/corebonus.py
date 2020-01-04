

class CoreBonus:
    """
    Class for core bonus data.
    NECESSARY PRE-WORK:
    * Ensure the paragraph of core bonuses is preceded and followed by empty lines.

    NECESSARY POST-WORK:
    * Add the "mounted_effect" fields to:
      * cb_auto_stabilizing_hardpoints
      * cb_overpower_caliber
      * cb_mount_retrofitting
    """

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

    def __str__(self):
        output = "\n============== CORE BONUS ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\nsource: {self.source}"
        output += f"\neffect: {self.effect}"
        output += f"\ndesc: {self.description}"
        return output

    def parse_text(self, raw):
        self.source = raw[0].strip()
        text = raw[1]

        self.name = text[0].strip()
        self.id = "cb_" + self.name.lower().replace(" ", "_").replace("-", "_").replace("'", "")
        self.description = text[1].strip()
        self.effect = text[2].strip()

    def to_dict(self):
        return dict([
            ("id", self.id),
            ("name", self.name),
            ("source", self.source),
            ("effect", self.effect),
            ("description", self.description)
        ])
