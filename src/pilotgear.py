#!/bin/python3
# -*- utf-8 -*-

from parseutil import *


class PilotGear:
    """
    Class for pilot gear data.
    NECESSARY PREP-WORK:
    * Separate pieces of gear with empty lines.
    * Heavy Signature weapon - put range/damage on same line as tags
    """

    START = ["Pilot Gear\n",
             "On missions, pilots can take one set",
             "The names and descriptions given for pilot gear"]
    END = ["Wilderness Survival Kit\n",
           "Gear",
           "This kit contains many essentials for surviving in hostile environments:"]

    PREFIX = "pg_"

    WEAPONS_SEC = "Archaic Melee\n"
    ARMOR_SEC = "Light Hardsuit\n"
    GEAR_SEC = "Corrective\n"

    TYPE_WEAPON = "weapon"
    TYPE_ARMOR = "armor"
    TYPE_GEAR = "gear"

    def __init__(self, raw_weapon=None, raw_armor=None, raw_gear=None):
        """
        Initializer for Pilot Gear. Can either create a blank instance,
        or initialize a weapon, armor, or gear.
        @param raw_weapon: (str, bool, bool): raw text, threat flag, range flag.
        @param raw_armor: str: raw text for armor.
        @param raw_gear: str: raw text for gear.
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
            self.parse_weapon(raw_weapon)
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

    def __str__(self):
        if self.type == PilotGear.TYPE_ARMOR:
            output = "\n============== PILOT ARMOR ===================="
            output += f"\nid: {self.id}"
            output += f"\ntype: {self.type}"
            output += f"\nname: {self.name}"
            output += f"\ndesc: {self.description}"
            output += f"\ntags: "
            for t in self.tags:
                output += f"\n  {t}"
            output += f"\nhp_bonus: {self.hp_bonus}"
            output += f"\narmor: {self.armor}"
            output += f"\nevasion: {self.evasion}"
            output += f"\nedef: {self.edef}"
            output += f"\nspeed: {self.speed}"
        elif self.type == PilotGear.TYPE_GEAR:
            output = "\n============== PILOT GEAR ===================="
            output += f"\nid: {self.id}"
            output += f"\ntype: {self.type}"
            output += f"\nname: {self.name}"
            output += f"\ndesc: {self.description}"
            output += f"\ntags: "
            for t in self.tags:
                output += f"\n  {t}"
            output += f"\nuses: {self.uses}"
        elif self.type == PilotGear.TYPE_WEAPON:
            output = "\n============== PILOT WEAPON ===================="
            output += f"\nid: {self.id}"
            output += f"\ntype: {self.type}"
            output += f"\nname: {self.name}"
            output += f"\ndesc: {self.description}"
            output += f"\ntags: "
            for t in self.tags:
                output += f"\n  {t}"
            output += f"\nrange: "
            for r in self.range:
                output += f"\n  {r}"
            output += f"\ndamage: "
            for d in self.damage:
                output += f"\n  {d}"

        return output

    def parse_weapon(self, raw_text):
        """
        Parse the text for the pilot weapon.
        @param raw_text: [str]: Text to parse.
        @return: None
        """
        self.type = PilotGear.TYPE_WEAPON
        # Parse name and id from first line.
        self.name = raw_text[0].strip().upper()
        self.id = gen_id(PilotGear.PREFIX, self.name)

        # Parse tags and stats on second line.
        line = raw_text[1].strip()
        div = line.find("[")
        tag_text = line[:div]
        stat_text = line[div:]
        self.parse_tags(tag_text)

        # Parse stats - range/threat and damage.
        stats = stat_text.split("[")
        for stat in stats:
            # Remove the other bracket
            stat = stat.replace("]", "")
            if stat.lower().startswith("range") or stat.lower().startswith("threat"):
                parts = stat.lower().split(" ")
                val = parts[1].strip()
                if val.isdecimal():
                    val = int(val)
                self.range.append(dict([("type", parts[0].strip().title()),
                                        ("val", val)]))
            elif stat.lower().endswith("damage"):
                parts = stat.lower().split(" ")
                val = parts[0].strip()
                if val.isdecimal():
                    val = int(val)
                if len(parts) == 2:
                    self.damage.append(dict([("type", "variable"),
                                             ("val", val)]))
                    self.effect = "When a signature weapon is acquired, choose its damage type – Explosive, Energy, or Kinetic."
                elif len(parts) == 3:
                    self.damage.append(dict([("type", parts[1].strip()),
                                             ("val", val)]))
                else:
                    print(f"Problem parsing pilot weapon damage: {parts}")

        self.description = raw_text[2].strip()

    def parse_armor(self, raw_text):
        """
        Parse the raw text for a pilot armor.
        @param raw_text: [str]: Text to parse.
        @return: None
        """
        self.type = PilotGear.TYPE_ARMOR
        # Parse name and id from first line.
        self.name = raw_text[0].strip().upper()
        self.id = gen_id(PilotGear.PREFIX, self.name)

        # Parse tags on 2nd line
        self.parse_tags(raw_text[1].strip())
        for tag in self.tags:
            if tag["id"] == "tg_flight" or tag["id"] == "tg_invisibility":
                self.tags.remove(tag)

        # 3rd and 4th lines are the stats
        stats = raw_text[2].strip() + raw_text[3].strip()
        stats = stats.split("[")
        for stat in stats:
            # Remove the closing bracket
            stat = stat.replace("]", "")
            parts = stat.lower().split(" ")
            if "hp" in parts:
                self.hp_bonus = int(parts[0].replace("+", ""))
            elif "armor" in parts:
                self.armor = int(parts[0])
            elif "evasion" in parts:
                self.evasion = int(parts[0])
            elif "e-defense" in parts:
                self.edef = int(parts[0])
            elif "speed" in parts:
                self.speed = int(parts[0])

        # Description is the 5th line
        self.description = raw_text[4].strip()

    def parse_gear(self, raw_text):
        """
        Parse the raw text for a pilot gear.
        @param raw_text: [str]: Text to parse.
        @return: None
        """
        self.type = PilotGear.TYPE_GEAR
        # Parse name and id from first line.
        self.name = raw_text[0].strip().upper()
        self.id = gen_id(PilotGear.PREFIX, self.name)

        # Parse tags from second line.
        self.parse_tags(raw_text[1].strip())

        # Combine remaining lines to create the description.
        self.description = raw_text[2].strip()
        if len(raw_text) > 3:
            for line in raw_text[3:]:
                if line.startswith("- "):
                    line = line.replace("- ", "<li>", 1).strip()
                self.description += "<br>"+line.strip()
            # Remove extraneous line breaks.
            self.description = self.description.replace("<br><li>", "<li>")

    def set_id(self, new_id):
        self.id = new_id

    def set_name(self, new_name):
        self.name = new_name

    def set_desc(self, new_desc):
        self.description = new_desc

    def parse_tags(self, tagline):
        """
        Parse the tags for the pilot gear.
        @param tagline: str: The line of text containing the tags.
        @return: None.
        """
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
                if not is_duplicate_tag(d, self.tags) and d["id"] != "tg_":
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