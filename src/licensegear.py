

class IMechGear:
    """
    Interface for mech gear, defining common methods.
    """
    def parse_tags(self, tagline):
        if "SP" in tagline:
            self.sp = int(tagline.split(",")[0].split(" ")[0])
            # Take the "X SP," substring off of the front.
            tagline = tagline.partition(",")[2]

        tags = tagline.split(",")
        for t in tags:
            if t != "-\n":
                words = t.strip().split(" ")
                # If the tag contains a number, parse it as 'val'.
                val = None
                t_text = ""
                for word in words:
                    if word.isdecimal():
                        val = int(word)
                    else:
                        t_text += " "+word
                t_text.strip()
                d = {"id": "tg_"+(t_text.strip().lower().replace(" ", "_").replace("(", "").replace(")", ""))}
                if val is not None:
                    d["val"] = val
                self.tags.append(d)


class Mod(IMechGear):
    """
    Class for weapon mods.
    NECESSARY PREP WORK:
    *
    """
    def __init__(self, raw_text=None):
        pass


class System(IMechGear):
    """
    Class for mech systems.
    NECESSARY PREP WORK:
    * Each system must be preceded and followed by an empty line.
    * Add a line containing "---" between the description and effect of each system.
      Systems which do not have this line are assumed to not have a description.
    """

    GMS_SYSTEMS = "GMS GENERAL MARKET SYSTEMS\n"
    GMS_FLIGHT = "GMS FLIGHT SYSTEMS\n"
    GMS_SYS_END = "You can fly when you BOOST or make a standard move; however"

    def __init__(self, raw=None):
        """
        Create a new system.
        @param raw: (str, [str]): source mfr, raw text.
        """
        self.id = ""
        self.name = ""
        self.type = "System"
        self.sp = 0
        self.tags = []
        self.source = ""
        self.license = ""
        self.license_level = ""
        self.effect = ""
        self.description = ""
        self.data_type = "system"
        self.aptitude = ""

        if raw is not None:
            self.source = raw[0]
            self.parse_text(raw[1])

    def __str__(self):
        output = "\n\n============== SYSTEM ===================="
        output += f"\nid: {self.id}"
        output += f"\nname: {self.name}"
        output += f"\ntype: {self.type}"
        output += f"\nsp: {self.sp}"
        output += f"\ntags:"
        for tag in self.tags:
            output += f"\n   {tag}"
        output += f"\nsource: {self.source}"
        output += f"\nlicense: {self.license}"
        output += f"\nll: {self.license_level}"
        output += f"\ndesc: {self.description}"
        output += f"\neffect: {self.effect}"
        output += f"\ndata_type: {self.data_type}"
        output += f"\naptitude: {self.aptitude}"
        return output

    def parse_text(self, raw_text):
        self.name = raw_text[0].strip()
        self.id = "ms_"+self.name.lower().replace(" ", "_").replace("/", "_").replace("-", "_").replace("'", "").replace("\"", "")

        self.parse_tags(raw_text[1])

        # Find the split between description and effect
        split = -1
        for i in range(len(raw_text)):
            if raw_text[i] == "---\n":
                split = i
                break
        if split > 0:
            for line in raw_text[2:split]:
                if self.description == "":
                    self.description = line.strip()
                else:
                    self.description += "<br>"+line.strip()
            for line in raw_text[split+1:]:
                if self.effect == "":
                    self.effect = line.strip()
                else:
                    self.effect += "<br>"+line.strip()
        else:  # No split means there is no description.
            for line in raw_text[2:]:
                if self.effect == "":
                    self.effect = line.strip()
                else:
                    self.effect += "<br>"+line.strip()

    def set_license(self, lic, level):
        """
        Set the license and level of the system.
        @param lic: str: frame license the system belongs to.
        @param level: int: level of the license the system belongs to.
        @return:
        """
        self.license = lic
        self.license_level = level

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "type": self.type,
                "sp": self.sp,
                "tags": self.tags,
                "source": self.source,
                "license": self.license,
                "license_level": self.license_level,
                "effect": self.effect,
                "description": self.description,
                "data_type": self.data_type,
                "aptitude": self.aptitude}


class Weapon(IMechGear):
    """
    Class for mech weapons.
    NECESSARY PREP WORK:
    * Each weapon must be preceded and followed by an empty line.
    """

    GMS_WEP_TABLE = "GMS MECH WEAPONS\n"
    GMS_WEP_END = "GMS GENERAL MARKET SYSTEMS\n"

    def __init__(self, raw_text=None):
        pass
