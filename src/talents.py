# NECESSARY PREP-WORK:
# Make sure that each talent is preceded by ONE empty line.


class Talent:
    START = ["ACE\n",
             "Every pilot brags about their abilities; ",
             "Whether you're a talented rookie"]
    END = ["- SABOT (2 charges): The attack ",
           "EFFICIENCY (RANK III): If you perform ",
           "\n"]

    """Class for talent data"""
    def __init__(self, raw_text=None):
        self.id = ""
        self.name = ""
        self.description = ""
        # list of 3 dicts with keys 'name' and 'description'
        self.ranks = [dict([("name", ""), ("description", "")]) for i in range(3)]

        if raw_text:
            self.parse_raw_text(raw_text)

    def parse_raw_text(self, raw_text):
        RANK = [u" (RANK I): ",
                u" (RANK II): ",
                u" (RANK III): "]

        name_line = -1
        rank_start = [-1, -1, -1]
        for i in range(len(raw_text)):
            line = raw_text[i].strip()
            # Name is the first non-empty line
            if self.name == "" and line != "":
                self.name = line
                self.id = "t_"+self.name.lower().replace(" ", "_")
                name_line = i
            # Don't look for the rest until the name is found
            elif 0 <= name_line < i:
                # Find the lines which contain the rank names
                for j in range(len(RANK)):
                    if RANK[j] in line:
                        rank_start[j] = i
        # Description starts line after name, and ends at line before rank 1.
        for line in raw_text[name_line+1:rank_start[0]]:
            self.description += line.strip()
        # Get ranks text
        for i in range(len(rank_start)):
            line = raw_text[rank_start[i]].strip()
            r_name_end = line.find(RANK[i])
            r_desc_start = r_name_end + len(RANK[i])
            self.ranks[i]["name"] = line[:r_name_end].strip()
            r_desc = line[r_desc_start:].strip()
            # Get the line the next rank starts on.
            if i < len(rank_start)-1:
                next_r = rank_start[i+1]
            # Last rank ends at the end of the raw text.
            else:
                next_r = len(raw_text)
            for line in raw_text[rank_start[i]+1:next_r]:
                # Put bulleted points on new line
                if line.startswith("- "):
                    r_desc += "<br>" + line.strip()
                else:
                    r_desc += " " + line.strip()
            self.ranks[i]["description"] = r_desc

        # Debugging printout
        # print("\n\n============== TALENT ====================")
        # print(f"rank start: {rank_start}")
        # print(f"id: {self.id}")
        # print(f"name: {self.name}")
        # print(f"desc: {self.description}\n")
        # print(f"ranks:")
        # for r in self.ranks:
        #     print(f"    name: {r['name']}")
        #     print(f"    desc: {r['description']}")

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