

class Skill:
    """
    Class for pilot skill data.
    """

    START = ["ACT UNSEEN OR UNHEARD\n",
             "Get somewhere or do something without",
             "APPLY FISTS TO FACES\n"]
    END = ["Use force or threats to make someone",
           "WORD ON THE STREET\n",
           "Get gossip, news, or hearsay from the streets,"]

    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.description = ""
        self.detail = ""
        self.family = ""

        if raw_text:
            self.parse_raw_text(raw_text)

    def parse_raw_text(self, raw_text):
        self.name = raw_text[0]
        self.id = "sk_"+self.name.lower().replace(" ", "_")
        self.description = raw_text[1]

        # Debugging printout
        print("\n============== TRIGGER ====================")
        print(f"id: {self.id}")
        print(f"name: {self.name}")
        print(f"desc: {self.description}")

    def set_id(self, new_id):
        self.id = new_id

    def set_name(self, new_name):
        self.name = new_name

    def set_desc(self, new_desc):
        self.description = new_desc

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "detail": self.detail,
                "family": self.family}
