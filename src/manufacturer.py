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

    GMS = ("GENERAL MASSIVE SYSTEMS\n", "General Massive Systems - GMS for short - is the galactic-standard supplier", "gms")
    IPSN = ("IPS-NORTHSTAR\n", "IPS-Northstar (IPS-N) was created ", "ips-n")
    SSC = ("SMITH-SHIMANO CORPRO\n", "Smith-Shimano Corpro (SSC) is the second-oldest ", "ssc")
    HORUS = ("HORUS\n", "HORUS is an oddity among the various pan-galactic", "horus")
    HA = ("HARRISON ARMORY\n", "Harrison Armory enjoys a galaxy-wide reputation for the quality", "ha")
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
        self.name = raw[0].strip()
        self.id = gen_id(Manufacturer.PREFIX, self.name)

        if raw[0] == Manufacturer.GMS[0]:
            desc_start = Manufacturer.GMS[1]
            self.logo = Manufacturer.GMS[2]
        elif raw[0] == Manufacturer.IPSN[0]:
            desc_start = Manufacturer.IPSN[1]
            self.logo = Manufacturer.IPSN[2]
        elif raw[0] == Manufacturer.SSC[0]:
            desc_start = Manufacturer.SSC[1]
            self.logo = Manufacturer.SSC[2]
        elif raw[0] == Manufacturer.HORUS[0]:
            desc_start = Manufacturer.HORUS[1]
            self.logo = Manufacturer.HORUS[2]
        elif raw[0] == Manufacturer.HA[0]:
            desc_start = Manufacturer.HA[1]
            self.logo = Manufacturer.HA[2]

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
        # Get the description
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
