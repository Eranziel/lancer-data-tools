#!/bin/python3
# -*- utf-8 -*-

"""Parses data from rulebook text"""

import argparse
import json
# import asyncio
from deepmerge import always_merger

from frame import Frame
from manufacturer import Manufacturer
from corebonus import CoreBonus
from licensegear import Mod, System, Weapon
from talents import Talent
from tags import Tag
from pilotgear import PilotGear
from skills import Skill
from statuses import Status
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
STATUSES = "../output/statuses.json"


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
                s_found = s_found and rawLines[i + j].startswith(start[j])
            if end_idx < 0:
                e_found = e_found and rawLines[i + j].startswith((end[j]))
            # Stop if a line doesn't match either the start or end delimeters.
            if not s_found and not e_found:
                break

        if s_found and start_idx < 0:
            start_idx = i
        if e_found and end_idx < 0:
            end_idx = i + j
        if start_idx >= 0 and end_idx >= 0:
            return start_idx, end_idx
    print(f"There was a problem! s{start_idx}, e{end_idx}")


def read_override(file_name):
    """
    Reads the override mask file and returns a list of dicts representing
    the contents.
    @param file_name: str: the name of the mask file.
    @return: [dict]: JSON from the mask file, converted to list of dicts.
    """
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
    """
    Applies the given mask data.
    @param original: dict: The parsed data to be overridden.
    @param mask: [dict]: The data read from the mask file.
    @return: dict: Returns a copy of original. Matching keys take the
    value from the mask, keys in the mask which aren't in original are
    added, and any list keys are merged.
    """
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
    """
    Adds elements from the mask which aren't present in the parsed data.
    @param js_list: [dict]: The parsed data.
    @param mask: [dict]: The data read from the mask file.
    @param prefix: str: The id prefix being handled.
    @return: [dict]: Returns a copy of js_list. If there are id's in mask
    which start with prefix and aren't present in js_list, they are inserted
    into the returned copy.
    """
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


def weapon_check(txt):
    """
    Check whether a text hunk is a weapon.
    @param txt: [str]: The text hunk to check.
    @return: bool: True if the hunk is a weapon.
    """
    result = False
    for line in txt:
        for rng in Weapon.RANGE:
            if "[" in line and "]" in line and rng in line:
                return True
        for dmg in Weapon.DAMAGE:
            if "[" in line and "]" in line and dmg in line:
                return True
    return result


def mod_check(txt):
    """
    Check whether a text hunk is a weapon mod.
    @param txt: [str]: The text hunk to check.
    @return: bool: True if the hunk is a weapon mod.
    """
    if len(txt) >= 2 and "Mod" in txt[1]:
        return True
    return False


def sys_check(txt):
    """
    Check whether a text hunk is a system.
    @param txt: [str]: The text hunk to check.
    @return: bool: True if the hunk is a system.
    """
    return not mod_check(txt) and not weapon_check(txt)


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
    parser.add_argument("-S", "--statuses", action="store_true",
                        help="Generate status/condition JSON.")
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
        rawTalents = rawLines[s:e + 1]
        talentHunks = []
        prev = 0
        for i in range(len(rawTalents)):
            if rawTalents[i] == "\n":
                talentHunks.append(rawTalents[prev:i])
                prev = i + 1
        # Get the final hunk.
        talentHunks.append(rawTalents[prev:])

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
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))
    if args.tags:
        inTags = False

        # Parse the text
        s, e = check_section(Tag.START, Tag.END)
        print(f"Tags start: {s}, end: {e}")
        rawTags = rawLines[s:e + 1]
        tags = []
        in_ignore = False
        for rt in rawTags:
            if not in_ignore and rt.startswith(Tag.FILT_IGN[0]):
                in_ignore = True
            elif in_ignore and rt.startswith(Tag.FILT_IGN[1]):
                in_ignore = False
            # Only process lines that have a colon near the start
            if ": " in rt[:40]:
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
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))
    if args.pilot_gear:
        inPilotGear = False

        # Parse the text
        s, e = check_section(PilotGear.START, PilotGear.END)
        print(f"Pilot Gear start: {s}, end: {e}")
        rawPilotGear = rawLines[s:e + 1]
        gearHunks = []
        pg = []
        prev = 0
        for i in range(len(rawPilotGear)):
            if rawPilotGear[i] == "\n":
                gearHunks.append(rawPilotGear[prev:i])
                prev = i + 1
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
                # Weapon profiles are all of length 3
                if len(g) == 3:
                    rw = (g)
                    pg.append(PilotGear(raw_weapon=rw))
            elif inArmor:
                # Armor profiles are all of length 5
                if len(g) == 5:
                    pg.append(PilotGear(raw_armor=g))
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
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))
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
        rawSkills = rawLines[s:e + 1]
        skills = []
        for i in range(len(rawSkills)):
            if rawSkills[i].isupper():
                skills.append(Skill(rawSkills[i:i + 2]))
        j = []
        for s in skills:
            j.append(apply_override(s.to_dict(), mask))
        add_missing_overrides(j, mask, Skill.PREFIX)
        print(f"Outputting JSON for {len(skills)} skills to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))
    if args.frames:
        inFrames = False

        # Parse the text
        s, e = check_section(Frame.START, Frame.END)
        print(f"Frames start: {s}, end: {e}")
        rawFrames = rawLines[s:e + 1]
        frameHunks = []
        frames = []
        manufacturers = []
        coreBonuses = []
        systems = []
        weapons = []
        mods = []
        prev = 0
        for i in range(len(rawFrames)):
            if rawFrames[i] == "\n":
                frameHunks.append(rawFrames[prev:i])
                prev = i + 1
        # Catch the last hunk
        frameHunks.append(rawFrames[prev:])
        # Strip out any empty hunks
        while [] in frameHunks:
            frameHunks.remove([])
        source = "NONE"
        gmsSec = "NONE"
        gmsWepDesc = ["" for i in range(4)]
        for hunk in frameHunks:
            # Keep track of which subsection we're in.
            if hunk[0] == Manufacturer.GMS[0]:
                source = Manufacturer.GMS[2]
                gmsSec = "NONE"
            elif hunk[0] == Manufacturer.IPSN[0]:
                source = Manufacturer.IPSN[2]
                gmsSec = "NONE"
            elif hunk[0] == Manufacturer.SSC[0]:
                source = Manufacturer.SSC[2]
                gmsSec = "NONE"
            elif hunk[0] == Manufacturer.HORUS[0]:
                source = Manufacturer.HORUS[2]
                gmsSec = "NONE"
            elif hunk[0] == Manufacturer.HA[0]:
                source = Manufacturer.HA[2]
                gmsSec = "NONE"
            elif hunk[0] == System.GMS_SYSTEMS:
                gmsSec = "Systems"
            elif hunk[0] == System.GMS_FLIGHT:
                gmsSec = "Flight"
            elif hunk[0] == Weapon.GMS_WEP_TABLE:
                gmsSec = "Weapons"
                # Get the description for the GMS weapons
                for line in hunk[1:]:
                    # GMS Type-I description
                    if Weapon.GMS_TYPES[0] in line:
                        gmsWepDesc[0] = hunk[1].strip() + "<br>" + line.strip()
                    # GMS Type-II descriptions
                    elif Weapon.GMS_TYPES[1] in line:
                        line = line.strip()
                        # Both descriptions start with the first sentence.
                        period = line.find(".")
                        charged = thermal = hunk[1].strip() + "<br>" + line[:period+1]
                        # Find the division between charged blades and thermal guns.
                        div = line.find(Weapon.GMS_T2_THERMAL)
                        # Finish charged blades string.
                        charged += line[period+1:div]
                        # Finish thermal guns string.
                        thermal += " " + line[div:]
                        gmsWepDesc[1] = charged
                        gmsWepDesc[2] = thermal
                    # GMS Type-III description
                    elif Weapon.GMS_TYPES[2] in line:
                        gmsWepDesc[3] = hunk[1].strip() + "<br>" + line.strip()

            # Determine what kind of data this hunk is for.
            #   Frames
            if Frame.CORE_STATS in hunk:
                frames.append(Frame(raw_text=hunk))
            #   Manufacturers
            elif hunk[0] in Manufacturer.TITLES:
                manufacturers.append(Manufacturer(raw=hunk))
            #   Core Bonuses
            elif CoreBonus.CORE in hunk[0]:
                txt = hunk[1:]
                cap_lines = []
                # Each core bonus is named by a line that is all upper case.
                # Find those lines and split the text into separate core bonuses
                # accordingly.
                for i in range(len(txt)):
                    if txt[i].isupper():
                        cap_lines.append(i)
                for i in range(len(cap_lines)):
                    if i < len(cap_lines)-1:
                        raw = (source, txt[cap_lines[i]:cap_lines[i+1]])
                    else:
                        raw = (source, txt[cap_lines[i]:])
                    coreBonuses.append(CoreBonus(raw=raw))
            #   Weapons
            elif gmsSec == "Weapons":
                # All GMS weapon entries are 5 lines
                if 3 <= len(hunk) <= 4:
                    weapons.append(Weapon(raw_text=hunk, gms=gmsWepDesc, src=source))
            elif weapon_check(hunk):
                weapons.append(Weapon(raw_text=hunk, gms=None, src=source,
                                      lic_table=frames[-1].license))
            #   Weapon Mods
            elif mod_check(hunk):
                mods.append(Mod(raw_text=hunk, src=source,
                                lic_table=frames[-1].license))
            #   Systems
            elif (gmsSec == "Systems"
                  or gmsSec == "Flight"):
                if len(hunk) >= 3 and hunk[0] != System.GMS_FLIGHT:
                    systems.append(System(raw_text=hunk, src=source))
                    if gmsSec == "Flight":
                        systems[-1].type = "Flight System"
            elif sys_check(hunk):
                systems.append(System(raw_text=hunk, src=source,
                                      lic_table=frames[-1].license))

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
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))

        # Create data output for manufactuers
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(MANUFACTURERS)
        j = []
        for mfr in manufacturers:
            j.append(apply_override(mfr.to_dict(), mask))
        add_missing_overrides(j, mask, Manufacturer.PREFIX)
        print(f"Outputting JSON for {len(manufacturers)} manufacturers to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))

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
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))

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
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))

        # Create data output for mods
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(MODS)
        j = []
        for mod in mods:
            j.append(apply_override(mod.to_dict(), mask))
            # Debugging printout
            # print("\n" + str(mod))
        add_missing_overrides(j, mask, Mod.PREFIX)
        print(f"Outputting JSON for {len(mods)} mods to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))

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
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))
    if args.statuses:
        pass
        # Create data output
        if args.stdout:
            dOut = DataOutput("stdout")
        else:
            dOut = DataOutput(STATUSES)
        inStatuses = False

        # Parse the text
        s, e = check_section(Status.START, Status.END)
        print(f"Statuses start: {s}, end: {e}")
        rawStatuses = rawLines[s:e + 1]
        statuses = []
        # Each new status starts with a line in upper case.
        cap_lines = []
        stat = False
        for i in range(len(rawStatuses)):
            if rawStatuses[i].isupper():
                cap_lines.append(i)
        for i in range(len(cap_lines)):
            idx = cap_lines[i]
            if rawStatuses[idx] == Status.START[0]:
                pass
            elif rawStatuses[idx] == Status.STATUS:
                stat = True
            elif rawStatuses[idx] == Status.CONDITION:
                stat = False
            else:
                if i < len(cap_lines) - 1:
                    statuses.append(Status(rawStatuses[idx:cap_lines[i+1]], stat))
                else:
                    statuses.append(Status(rawStatuses[idx:], stat))
        j = []
        for s in statuses:
            j.append(apply_override(s.to_dict(), mask))
        add_missing_overrides(j, mask, Status.PREFIX)
        print(f"Outputting JSON for {len(statuses)} statuses to {dOut.target}")
        dOut.write(json.dumps(j, indent=2, separators=(',', ': '), ensure_ascii=False))
