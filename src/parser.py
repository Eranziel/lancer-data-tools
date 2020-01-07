#!python

"""Parses data from rulebook text"""

import argparse
import json
# import asyncio
from deepmerge import always_merger

from frame import Frame
from corebonus import CoreBonus
from licensegear import Mod, System, Weapon
from talents import Talent
from tags import Tag
from pilotgear import PilotGear
from skills import Skill
from dataoutput import DataOutput

rawLines = []

# Output file names
CORE_BONUSES = "../output/core_bonuses.json"
FRAMES = "../output/frames.json"
MANUFACTURERS = "../output/manufacturers.json"
MODS = "../output/mods.json"
PILOT_GEAR = "../output/pilot_gear.json"
SKILLS = "../output/skills.json"
SYSTEMS = "../output/systems.json"
TAGS = "../output/tags.json"
TALENTS = "../output/talents.json"
WEAPONS = "../output/weapons.json"


def check_section(start, end):
    """
    Checks which lines a section spans.
    @param start: [str]: a set of lines defining the start of the section.
    @param end: [str]: a set of lines defining the end of the section.
    @return: (int, int): the start and end indexes within the raw text.
    """
    start_idx = -1
    end_idx = -1
    for i in range(len(rawLines)):
        s_found = True
        e_found = True
        for j in range(len(start)):
            # If lines i through i+j all match start, record the starting line.
            if start_idx < 0:
                s_found = s_found and rawLines[i+j].startswith(start[j])
            if end_idx < 0:
                e_found = e_found and rawLines[i+j].startswith((end[j]))
            # Stop if a line doesn't match either the start or end delimeters.
            if not s_found and not e_found:
                break

        if s_found and start_idx < 0:
            start_idx = i
        if e_found and end_idx < 0:
            end_idx = i+j
        if start_idx >= 0 and end_idx >= 0:
            return start_idx, end_idx
    print(f"There was a problem! s{start_idx}, e{end_idx}")


def read_override(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as mask_file:
            file_lines = mask_file.readlines()
        file_str = ""
        for line in file_lines:
            file_str += line
        return json.loads(file_str)
    except FileNotFoundError:
        print(f"Mask file {file_name} not found.")
        exit(1)


def apply_override(original, mask):
    result = original
    # Overrides need an ID to reference
    if "id" in original.keys() and mask != []:
        for m in mask:
            # If there is a matching ID in the mask, insert/replace
            #   all other elements of the mask into the original.
            if m["id"] == original["id"]:
                result = always_merger.merge(original, m)
    return result


def add_missing_overrides(js_list, mask, prefix):
    if mask == [] or js_list == []:
        return
    for m in mask:
        if m["id"].startswith(prefix):
            present = False
            for j in js_list:
                if "id" in j.keys() and j["id"] == m["id"]:
                    present = True
                    break
            if not present:
                js_list.append(m)


def weapon_check(text):
    result = False
    for line in text:
        if line.startswith("---"):
            return False
        if line.startswith(Weapon.RANGE) or line.startswith(Weapon.THREAT):
            result = True
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", help="Output to stdout instead of file.")
    parser.add_argument("-t", "--talents", action="store_true",
                        help="Generate talents JSON.")
    parser.add_argument("-T", "--tags", action="store_true",
                        help="Generate tag data JSON.")
    parser.add_argument("-p", "--pilot-gear", action="store_true",
                        help="Generate pilot gear JSON.")
    parser.add_argument("-s", "--skills", action="store_true",
                        help="Generate skill trigger JSON.")
    parser.add_argument("-f", "--frames", action="store_true",
                        help="Generate frame, core bonus, and mech gear JSON.")
    parser.add_argument("-m", "--mask", nargs=1,
                        help="Specify a mask file with overrides for specific id's.")
    parser.add_argument("raw", help="raw text input file")
    args = parser.parse_args()

    # Read raw file into memory - need to watch memory usage
    try:
        with open(args.raw, 'r', encoding='utf-8') as rawFile:
            rawLines = rawFile.readlines()
    except FileNotFoundError:
        print(f"Raw input file {rawFile} not found.")
        exit(1)

    # Read the mask file.
    if args.mask:
        mask = read_override(args.mask[0])
    else:
        mask = []

    if args.talents:
        inTalents = False

        # Parse the text
        s, e = check_section(Talent.START, Talent.END)
        print(f"Talents start: {s}, end: {e}")
        rawTalents = rawLines[s:e+1]
        talentHunks = []
        prev = 0
        for i in range(len(rawTalents)):
            if rawTalents[i] == "\n":
                talentHunks.append(rawTalents[prev:i])
                prev = i+1

        talents = []
        for t in talentHunks:
            talents.append(Talent(t))

        # Create data output
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(TALENTS)
        # Output results
        j = []
        for t in talents:
            j.append(apply_override(t.to_dict(), mask))
        add_missing_overrides(j, mask, Talent.PREFIX)
        print(f"Outputting JSON for {len(talents)} talents to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))
    if args.tags:
        inTags = False

        # Parse the text
        s, e = check_section(Tag.START, Tag.END)
        print(f"Tags start: {s}, end: {e}")
        rawTags = rawLines[s:e+1]
        tags = []
        in_ignore = False
        for rt in rawTags:
            if not in_ignore and rt == Tag.FILT_IGN[0]:
                in_ignore = True
            elif in_ignore and rt == Tag.FILT_IGN[1]:
                in_ignore = False
            # Only process lines that start with a bullet
            if rt.startswith("- "):
                tag = Tag(rt.strip())
                if in_ignore:
                    tag.set_filter(True)
                tags.append(tag)
        # Create data output
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(TAGS)
        # Output results
        j = []
        for t in tags:
            j.append(apply_override(t.to_dict(), mask))
        add_missing_overrides(j, mask, Tag.PREFIX)
        print(f"Outputting JSON for {len(tags)} tags to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))
    if args.pilot_gear:
        inPilotGear = False

        # Parse the text
        s, e = check_section(PilotGear.START, PilotGear.END)
        print(f"Pilot Gear start: {s}, end: {e}")
        rawPilotGear = rawLines[s:e+1]
        gearHunks = []
        pg = []
        prev = 0
        for i in range(len(rawPilotGear)):
            if rawPilotGear[i] == "\n":
                gearHunks.append(rawPilotGear[prev:i])
                prev = i+1
        # Catch the last hunk
        gearHunks.append(rawPilotGear[prev:])

        # Initialize processing flags
        inWeapons = False
        inArmor = False
        inGear = False
        r_range = False
        r_threat = False
        for g in gearHunks:
            # Check whether we're in a new section
            for line in g:
                if line == PilotGear.WEAPONS_SEC:
                    print("Entering pilot weapons section")
                    inWeapons = True
                    inArmor = False
                    inGear = False
                elif line == PilotGear.ARMOR_SEC:
                    print("Entering pilot armor section")
                    inWeapons = False
                    inArmor = True
                    inGear = False
                elif line == PilotGear.GEAR_SEC:
                    print("Entering pilot gear section")
                    inWeapons = False
                    inArmor = False
                    inGear = True
            # Parse pilot weapons
            if inWeapons:
                # Weapon profiles are all of length 4
                if len(g) == 4:
                    rw = (g, r_threat, r_range)
                    pg.append(PilotGear(raw_weapon=rw))
                # If it's less than 4 lines, it could be the descriptions.
                #   Check the start of each line against the name of each weapon
                #   to see if it is that weapon's description.
                else:
                    # Reset the range/threat flags at the next section which
                    #   isn't a weapon.
                    r_range = False
                    r_threat = False
                    for line in g:
                        # Check to see whether this line is the threat/range
                        #   header for a table of weapons.
                        if line == "Threat\n":
                            r_range = False
                            r_threat = True
                        elif line == "Range\n":
                            r_range = True
                            r_threat = False
                        for p in pg:
                            # If the line starts with the name of a weapon,
                            #   it's the description for that weapon.
                            if (p.type == PilotGear.TYPE_WEAPON and
                                    line.lower().startswith(p.name.lower())):
                                desc_start = line.find(":") + 1
                                if desc_start > 0:
                                    desc = line[desc_start:].strip()
                                else:
                                    desc = line.strip()
                                p.set_desc(desc)
                                break
            elif inArmor:
                # Armor profiles are all of length 7
                if len(g) == 7:
                    pg.append(PilotGear(raw_armor=g))
                else:
                    # Check for an item description
                    for line in g:
                        for p in pg:
                            if (p.type == PilotGear.TYPE_ARMOR and
                                    line.lower().startswith(p.name.lower())):
                                desc_start = line.find(":") + 1
                                if desc_start > 0:
                                    desc = line[desc_start:].strip()
                                else:
                                    desc = line.strip()
                                p.set_desc(desc)
                                break

            elif inGear:
                # Gear profiles are all of length > 1
                if len(g) > 1:
                    pg.append(PilotGear(raw_gear=g))

        # Create data output
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(PILOT_GEAR)
        # Output results
        j = []
        for p in pg:
            j.append(apply_override(p.to_dict(), mask))
        add_missing_overrides(j, mask, PilotGear.PREFIX)
        print(f"Outputting JSON for {len(pg)} pieces of pilot gear to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))
    if args.skills:
        # Create data output
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(SKILLS)
        inSkills = False

        # Parse the text
        s, e = check_section(Skill.START, Skill.END)
        print(f"Skills start: {s}, end: {e}")
        rawSkills = rawLines[s:e+1]
        skills = []
        for i in range(len(rawSkills)):
            if rawSkills[i].isupper():
                skills.append(Skill(rawSkills[i:i+2]))
        j = []
        for s in skills:
            j.append(apply_override(s.to_dict(), mask))
        add_missing_overrides(j, mask, Skill.PREFIX)
        print(f"Outputting JSON for {len(skills)} skills to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))
    if args.frames:
        inFrames = False

        # Parse the text
        s, e = check_section(Frame.START, Frame.END)
        print(f"Frames start: {s}, end: {e}")
        rawFrames = rawLines[s:e+1]
        frameHunks = []
        frames = []
        coreBonuses = []
        systems = []
        weapons = []
        mods = []
        prev = 0
        for i in range(len(rawFrames)):
            if rawFrames[i] == "\n":
                frameHunks.append(rawFrames[prev:i])
                prev = i+1
        # Catch the last hunk
        frameHunks.append(rawFrames[prev:])
        # Strip out any empty hunks
        while [] in frameHunks:
            frameHunks.remove([])
        source = "NONE"
        gmsSec = "NONE"
        gmsWepDesc = ""
        for hunk in frameHunks:
            # print(f"\nHunk:\n{hunk}")
            # Keep track of which subsection we're in.
            if hunk[0] == CoreBonus.GMS:
                source = "GMS"
                gmsSec = "NONE"
            elif hunk[0] == CoreBonus.IPSN:
                source = "IPS-N"
                gmsSec = "NONE"
            elif hunk[0] == CoreBonus.SSC:
                source = "SSC"
                gmsSec = "NONE"
            elif hunk[0] == CoreBonus.HORUS:
                source = "HORUS"
                gmsSec = "NONE"
            elif hunk[0] == CoreBonus.HA:
                source = "HA"
                gmsSec = "NONE"
            elif hunk[0] == System.GMS_SYSTEMS:
                gmsSec = "Systems"
            elif hunk[0] == System.GMS_FLIGHT:
                gmsSec = "Flight"
            elif hunk[0] == Weapon.GMS_WEP_TABLE:
                gmsSec = "Weapons"
                # Get the description for the GMS weapons
                for line in hunk[1:]:
                    # Ignore lines with only one word
                    if len(line.split(" ")) > 1:
                        if gmsWepDesc == "":
                            gmsWepDesc = line.strip()
                        else:
                            gmsWepDesc += "<br>"+line.strip()

            # Determine what kind of data this hunk is for.
            #   Frames
            if Frame.CORE_STATS in hunk:
                frames.append(Frame(raw_text=hunk))
            #   Core Bonuses
            elif CoreBonus.CORE in hunk[0]:
                text = hunk[1:]
                for i in range(len(text)):
                    if text[i].isupper():
                        raw = (source, text[i:i + 3])
                        coreBonuses.append(CoreBonus(raw=raw))
            #   Weapons
            elif gmsSec == "Weapons":
                # All GMS weapon entries are 5 lines
                if len(hunk) == 5:
                    weapons.append(Weapon(raw_text=hunk, gms=gmsWepDesc, src=source))
            elif weapon_check(hunk):
                weapons.append(Weapon(raw_text=hunk, gms=None, src=source,
                                      lic_table=frames[-1].license))
            #   Weapon Mods

            #   Systems
            elif (gmsSec == "Systems"
                  or gmsSec == "Flight"):
                if len(hunk) >= 3 and hunk[0] != System.GMS_FLIGHT:
                    systems.append(System(raw=hunk, src=source))
                    if gmsSec == "Flight":
                        systems[-1].type = "Flight System"

        # Create data output for frames
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(FRAMES)
        j = []
        for frame in frames:
            j.append(apply_override(frame.to_dict(), mask))
        add_missing_overrides(j, mask, Frame.PREFIX)
        print(f"Outputting JSON for {len(frames)} frames to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))

        # Create data output for core bonuses
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(CORE_BONUSES)
        j = []
        for cb in coreBonuses:
            j.append(apply_override(cb.to_dict(), mask))
        add_missing_overrides(j, mask, CoreBonus.PREFIX)
        print(f"Outputting JSON for {len(coreBonuses)} core bonuses to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))

        # Create data output for weapons
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(WEAPONS)
        j = []
        for weapon in weapons:
            j.append(apply_override(weapon.to_dict(), mask))
            # Debugging printout
            # print("\n" + str(weapon))
        add_missing_overrides(j, mask, Weapon.PREFIX)
        print(f"Outputting JSON for {len(weapons)} weapons to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))

        # Create data output for systems
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(SYSTEMS)
        j = []
        for system in systems:
            j.append(apply_override(system.to_dict(), mask))
            # Debugging printout
            # print("\n" + str(system))
        add_missing_overrides(j, mask, System.PREFIX)
        print(f"Outputting JSON for {len(systems)} systems to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': ')))
