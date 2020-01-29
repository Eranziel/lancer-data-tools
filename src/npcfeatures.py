#!/bin/python3
# -*- utf-8 -*-

from parseutil import *
from licensegear import Weapon


def new_npc_feature(raw):
    tag_line = raw[1].strip().lower()
    if "reaction" in tag_line:
        return NPCReaction(raw)
    elif "quick tech" in tag_line or "full tech" in tag_line:
        return NPCTech(raw)
    elif "system" in tag_line:
        return NPCSystem(raw)
    elif "trait" in tag_line or "template feature" in tag_line:
        return NPCTrait(raw)
    else:
        for line in raw:
            if "damage" in line.lower() or "heat" in line.lower() or "burn" in line.lower():
                return NPCWeapon(raw)
    feat = NPCFeature(raw)
    print(f"Couldn't identify NPC feature type, returning generic feature:\n{feat}")
    return feat


class NPCFeature:
    """
    Class for NPC features.
    """

    PREFIX = "npcf_"

    BASE_SYS = "base systems\n"
    OPT_SYS = "optional systems\n"

    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.origin = dict([
            ("type", ""),
            ("name", ""),
            ("base", True)
        ])
        self.type = ""
        self.effect = ""
        self.tags = []

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC FEATURE ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        for key in self.origin:
            output += f"\n   {key}: {self.origin[key]}"
        output += f"\ntype: {self.type}"
        output += f"\neffect: {self.effect}"
        return output

    def set_origin(self, o_type, name, base):
        self.origin["type"] = o_type
        self.origin["name"] = name
        self.origin["base"] = base

    def parse_text(self, raw):
        self.name = raw[0].strip().upper()
        self.id = gen_id(NPCFeature.PREFIX, self.name)

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "origin": self.origin,
                "type": self.type,
                "effect": self.effect,
                "tags": self.tags}

    def parse_tag(self, tag_text):
        """
        Parse tags for NPC feature.
        @param tag_text: str: The text for the tag.
        @return: None.
        """
        t = tag_text.strip()
        if t != "-":
            # 1 slash is x/turn or x/round
            if t.count("/") == 1:
                num, slash, t_text = t.strip().partition("/")
                # If there is a number before the slash, parse it as 'val'.
                val = None
                if num.isdecimal():
                    val = int(num)
                # If it wasn't a number, parse the whole text as a regular tag.
                else:
                    t_text = t
            else:
                # If the tag contains a number, parse it as 'val'.
                val = None
                t_text = ""
                for word in t.strip().split(" "):
                    if "+" in word:
                        word = word.replace("+", "")
                    if word.isdecimal():
                        val = int(word)
                    elif is_die_roll(word) or "/" in word:
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


class NPCWeapon(NPCFeature):
    """
    Class for NPC weapons.
    """

    def __init__(self, raw_text=None):
        super().__init__()
        self.w_type = ""
        self.attack_bonus = [0 for i in range(3)]
        self.accuracy = [0 for i in range(3)]
        self.damage = []
        self.range = []
        self.on_hit = ""
        self.type = "Weapon"

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC WEAPON ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        for key in self.origin:
            output += f"\n   {key}: {self.origin[key]}"
        output += f"\ntype: {self.type}"
        output += f"\natk_bonus: {self.attack_bonus}"
        output += f"\naccuracy: {self.accuracy}"
        output += f"\ndamage:"
        for d in self.damage:
            output += f"\n   {d}"
        output += f"\nrange:"
        for key in self.range:
            output += f"\n   {key}: {self.range[key]}"
        output += f"\non_hit: {self.on_hit}"
        output += f"\neffect: {self.effect}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        return output

    def parse_text(self, raw):
        super().parse_text(raw)
        self.parse_tags(raw[1])
        self.parse_stats(raw[2])
        if len(raw) > 3:
            if raw[3].lower().startswith("on hit:"):
                self.on_hit = raw[3][raw[3].find(":")+1:].strip()
                if len(raw) > 4:
                    self.effect = combine_lines(raw[4:])
            else:
                self.effect = combine_lines(raw[3:])

    def parse_tags(self, tag_line):
        tags = [t.strip() for t in tag_line.split(",")]
        for t in tags:
            words = t.split(" ")
            if words[0].title() in Weapon.MOUNTS:
                self.w_type = t.strip()
            elif "accuracy" in t.lower():
                self.parse_accuracy(t)
            elif "difficulty" in t.lower():
                self.parse_difficulty(t)
            elif "+" in t:
                self.parse_atk_bonus(t)
            else:
                self.parse_tag(t)

    def parse_atk_bonus(self, t):
        val = t.replace("+", "").strip()
        if "/" in val:
            val = [int(v) for v in t.strip().replace("+", "").split("/")]
        else:
            val = [int(val) for i in range(3)]
        self.attack_bonus = val

    def parse_accuracy(self, t):
        val = t.lower().replace("accuracy", "").strip()
        if "/" in val:
            val = [int(v) for v in val.strip().replace("+", "").split("/")]
        else:
            val = [int(val) for i in range(3)]
        self.accuracy = val

    def parse_difficulty(self, t):
        val = t.lower().replace("difficulty", "").strip()
        if "/" in val:
            val = [-int(v) for v in val.strip().replace("+", "").split("/")]
        else:
            val = [-int(val) for i in range(3)]
        self.accuracy = val

    def parse_stats(self, line):
        """
        Parse the range and damage spec line.
        @param line: str: The line with range and damage.
        @return: None.
        """
        parts = [p.replace("[", "").strip() for p in line.strip().split("]")]
        parts.remove("")
        for part in parts:
            words = [w.strip() for w in part.split(" ")]

            # Parse range stat
            if words[0].lower() in Weapon.RANGE:
                if " or " in part:
                    parts.append(part[part.rfind(" or ")+4:])

                r_type = words[0].title()
                val = words[1]
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
                    if harm in part.lower():
                        dmg = True
                        break
                # Parse damage stat
                if dmg:
                    d_type = ""
                    val = []
                    # If the damage stat has "or" in it, it's variable
                    if " or " in part:
                        d_type = "variable"
                    for word in words:
                        word = word.strip()

                        if word.isdecimal():
                            val = [int(word) for i in range(3)]
                        elif "/" in word:
                            val = [int(v.strip()) for v in word.split("/")]
                        elif word != "damage" and word != "+":
                            d_type = word

                        if len(val) > 0 and d_type != "":
                            d = dict([
                                ("type", d_type),
                                ("damage", val)
                            ])
                            self.damage.append(d)
                            d_type = ""
                            val = []

    def to_dict(self):
        d = super().to_dict()
        d["weapon_type"] = self.w_type
        d["attack_bonus"] = self.attack_bonus
        for x in self.accuracy:
            if x != 0:
                d["accuracy"] = self.accuracy
                break
        d["damage"] = self.damage
        d["range"] = self.range
        d["on_hit"] = self.on_hit
        d["tags"] = self.tags
        return d


class NPCTech(NPCFeature):
    """
    Class for NPC tech actions.
    """

    def __init__(self, raw_text=None):
        super().__init__()
        self.t_type = ""
        self.attack_bonus = []
        self.accuracy = []
        self.type = "Tech"

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC TECH ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        for key in self.origin:
            output += f"\n   {key}: {self.origin[key]}"
        output += f"\ntype: {self.type}"
        output += f"\ntech_type: {self.t_type}"
        output += f"\naccuracy: {self.attack_bonus}"
        output += f"\neffect: {self.effect}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        return output

    def parse_text(self, raw):
        super().parse_text(raw)
        self.parse_tags(raw[1])
        self.effect = combine_lines(raw[2:])

    def parse_tags(self, tag_line):
        tags = [t.strip() for t in tag_line.split(",")]
        for t in tags:
            if "recharge" in t.lower():
                self.parse_tag(t)
            elif "accuracy" in t.lower():
                self.parse_accuracy(t)
            elif "difficulty" in t.lower():
                self.parse_difficulty(t)
            elif "+" in t:
                self.parse_atk_bonus(t)
            else:
                self.parse_tag(t)
        for t in self.tags:
            if t['id'] == "tg_quick_tech":
                self.t_type = "Quick"
                break
            if t['id'] == "tg_full_tech":
                self.t_type = "Full"
                break

    def parse_atk_bonus(self, t):
        val = t.replace("+", "").strip()
        if "/" in val:
            val = [int(v) for v in t.strip().replace("+", "").split("/")]
        else:
            val = [int(val) for i in range(3)]
        self.attack_bonus = val

    def parse_accuracy(self, t):
        val = t.lower().replace("accuracy", "").strip()
        if "/" in val:
            val = [int(v) for v in val.strip().replace("+", "").split("/")]
        else:
            val = [int(val) for i in range(3)]
        self.accuracy = val

    def parse_difficulty(self, t):
        val = t.lower().replace("difficulty", "").strip()
        if "/" in val:
            val = [-int(v) for v in val.strip().replace("+", "").split("/")]
        else:
            val = [-int(val) for i in range(3)]
        self.accuracy = val

    def to_dict(self):
        d = super().to_dict()
        d["tech_type"] = self.t_type
        if self.attack_bonus:
            d["attack_bonus"] = self.attack_bonus
        for x in self.accuracy:
            if x != 0:
                d["accuracy"] = self.accuracy
                break
        return d


class NPCTrait(NPCFeature):
    """
    Class for NPC traits.
    """

    def __init__(self, raw_text=None):
        super().__init__()
        self.bonus = dict([])
        self.type = "Trait"

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC TRAIT ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        for key in self.origin:
            output += f"\n   {key}: {self.origin[key]}"
        output += f"\ntype: {self.type}"
        output += f"\neffect: {self.effect}"
        output += f"\nbonus:"
        for key in self.bonus.keys():
            output += f"\n   {key}: {self.bonus[key]}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        return output


class NPCSystem(NPCFeature):
    """
    Class for NPC systems.
    """

    def __init__(self, raw_text=None):
        super().__init__()
        self.bonus = dict([])
        self.type = "System"

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC SYSTEM ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        for key in self.origin:
            output += f"\n   {key}: {self.origin[key]}"
        output += f"\ntype: {self.type}"
        output += f"\neffect: {self.effect}"
        output += f"\nbonus:"
        for key in self.bonus.keys():
            output += f"\n   {key}: {self.bonus[key]}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        return output

    def parse_text(self, raw):
        super().parse_text(raw)
        self.parse_tags(raw[1])
        self.effect = combine_lines(raw[2:])

    def parse_tags(self, tag_line):
        tags = tag_line.split(",")
        try:
            tags.remove("System")
            tags.remove("Trait")
            tags.remove("Template Feature")
        except ValueError:
            pass  # If the above items aren't in tags, we'll get a ValueError.
        for t in tags:
            self.parse_tag(t)


class NPCReaction(NPCFeature):
    """
    Class for NPC reactions.
    """

    def __init__(self, raw_text=None):
        super().__init__()
        self.trigger = ""
        self.type = "Reaction"

        if raw_text:
            self.parse_text(raw_text)

    def __str__(self):
        output = "\n============== NPC REACTION ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        for key in self.origin:
            output += f"\n   {key}: {self.origin[key]}"
        output += f"\ntype: {self.type}"
        output += f"\ntrigger: {self.trigger}"
        output += f"\neffect: {self.effect}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        return output

