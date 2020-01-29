#!/bin/python3
# -*- utf-8 -*-


def gen_id(prefix, name):
    """
    Generate item ID from its name.
    @param prefix: str: The prefix for this data type.
    @param name: str: The item's name.
    @return: str: The generated id. Should only contain lowercase alphanumeric and _.
    """
    return prefix + name.strip().lower().replace(" ", "_").replace("/", "_").\
        replace("-", "_").replace("-", "_").replace("'", "").replace("’", "").\
        replace("“", "").replace("”", "").replace("\"", "").replace("(", "").\
        replace(")", "").replace(",", "").replace("!", "")


def combine_lines(lines, check_horus=False):
    """
    Combine the given lines into one string. Converts newlines to <br> tags,
    and adds <li> tags to the start of lines that start with a "- ".
    @param lines: [str]: The lines to combine.
    @param check_horus: bool: Flag for whether to check for Horus text (encloded in
    square brackets) and wrap it in appropriate tags.
    @return: str: The combined lines.
    """
    result = ""
    for line in lines:
        line = line.strip()
        if line.startswith("- "):
            line = line.replace("- ", "<li>", 1)
        elif line.startswith("– "):
            line = line.replace("– ", "<li>", 1)

        if check_horus and line.startswith("[") and line.endswith("]"):
            line = "<span class='ra-quiet'>"+line+"</span>"

        if result == "":
            result = line.strip()
        else:
            result += "<br>"+line.strip()
    result = result.replace("<br><li>", "<li>").strip()
    return result


def is_duplicate_tag(tag, tags):
    """
    Check whether a tag is already in a list of tags. Only checks the "id" key of
    the tag dicts.
    @param tag: dict: The new tag.
    @param tags: [dict]: The list of existing tags.
    @return: True if tag's "id" value matches that of one in tags.
    """
    if "id" not in tag.keys():
        return False
    for t in tags:
        if "id" in t.keys() and t["id"] == tag["id"]:
            return True
    return False


def is_die_roll(check_str):
    """
    Evaluate whether a string represents a die roll.
    @param check_str: The string to check.
    @return: True if the string represents a roll. Format is [#]d#[+#], where each
       instance of # is an integer. Portions within [] are optional.
    """
    d_ind = -1
    p_ind = -1
    if "d" in check_str:
        d_ind = check_str.find("d")
    if "+" in check_str:
        p_ind = check_str.find("+")

    num_dice = ""
    size_dice = ""
    flat_bonus = ""
    if d_ind == 0:
        num_dice = "1"
        if p_ind > 0:
            size_dice = check_str[d_ind+1:p_ind]
            flat_bonus = check_str[p_ind+1:]
        else:
            size_dice = check_str[d_ind+1:]
    elif d_ind > 0:
        num_dice = check_str[:d_ind]
        if p_ind > 0:
            size_dice = check_str[d_ind+1:p_ind]
            flat_bonus = check_str[p_ind+1:]
        else:
            size_dice = check_str[d_ind+1:]
    if flat_bonus == "":
        flat_bonus = "0"

    return num_dice.isdecimal() and size_dice.isdecimal() and flat_bonus.isdecimal()

