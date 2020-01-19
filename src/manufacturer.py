# /bin/python3
# -*- utf-8 -*-

from parseutil import *


class Manufacturer:
    """
    Class for manufacturer entry.
    NECESSARY PREP WORK:
    * None yet.
    """

    PREFIX = "mfr_"

    GMS = ("General Massive Systems\n", "General Massive Systems – GMS for short –", "GMS")
    IPSN = ("IPS-Northstar\n", "IPS-Northstar (IPS-N) was created ", "IPS-N")
    SSC = ("Smith-Shimano Corpro\n", "Smith-Shimano Corpro (SSC) is the second-oldest ", "SSC")
    HORUS = ("HORUS\n", "HORUS is an oddity among the various pan-galactic", "HORUS")
    HA = ("Harrison Armory\n", "Harrison Armory enjoys a galaxy-wide reputation for the quality", "HA")
    TITLES = [GMS[0], IPSN[0], SSC[0], HORUS[0], HA[0]]

    def __init__(self, raw=""):
        self.id = ""
        self.name = ""
        self.logo = ""
        self.color = ""
        self.quote = ""
        self.description = ""

        if raw != "":
            self.parse_text(raw)

    def parse_text(self, raw):
        self.name = raw[0].strip().upper()
        # self.id = gen_id(Manufacturer.PREFIX, self.name)

        if raw[0] == Manufacturer.GMS[0]:
            desc_start = Manufacturer.GMS[1]
            self.id = Manufacturer.GMS[2]
        elif raw[0] == Manufacturer.IPSN[0]:
            desc_start = Manufacturer.IPSN[1]
            self.id = Manufacturer.IPSN[2]
        elif raw[0] == Manufacturer.SSC[0]:
            desc_start = Manufacturer.SSC[1]
            self.id = Manufacturer.SSC[2]
        elif raw[0] == Manufacturer.HORUS[0]:
            desc_start = Manufacturer.HORUS[1]
            self.id = Manufacturer.HORUS[2]
        elif raw[0] == Manufacturer.HA[0]:
            desc_start = Manufacturer.HA[1]
            self.id = Manufacturer.HA[2]

        self.logo = self.id.lower()

        # Find the start of the description.
        desc = 0
        for i in range(len(raw)):
            line = raw[i]
            if line.startswith(desc_start):
                desc = i
                break
        # Get the quote
        for line in raw[1:desc]:
            if self.quote == "":
                self.quote = "<i>" + line.strip()
            else:
                self.quote += "<br>" + line.strip()
        self.quote += "</i>"
        if self.quote.startswith("<i>[") and self.quote.endswith("]</i>"):
            self.quote = self.quote.replace("<i>", "<code class='horus'>").\
                replace("</i>", "</code>")
        # Get the description
        # self.description = combine_lines(raw[desc:])
        for line in raw[desc:]:
            if self.description == "":
                self.description = line.strip()
            else:
                self.description += "<br><br>" + line.strip()

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "logo": self.logo,
                "color": self.color,
                "quote": self.quote,
                "description": self.description}
