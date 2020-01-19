#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


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

    PREFIX = "cb_"

    CORE = "CORE BONUSES\n"
    GMS = "General Massive Systems\n"
    IPSN = "IPS-Northstar\n"
    SSC = "Smith-Shimano Corpro\n"
    HORUS = "HORUS\n"
    HA = "Harrison Armory\n"

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
        """
        Parse the text for a core bonus.
        @param raw: (str, [str]): First index is the source manufacturer.
        Second index is the text to parse.
        @return: None.
        """
        self.source = raw[0].strip()
        text = raw[1]

        self.name = text[0].strip().upper()
        self.id = gen_id(CoreBonus.PREFIX, self.name)
        self.description = combine_lines(text[1:-1])
        self.effect = text[-1].strip()

    def to_dict(self):
        return dict([
            ("id", self.id),
            ("name", self.name),
            ("source", self.source),
            ("effect", self.effect),
            ("description", self.description)
        ])
