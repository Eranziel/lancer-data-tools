#!/bin/python3
# -*- utf-8 -*-


def gen_id(prefix, name):
    return prefix + name.strip().lower().replace(" ", "_").replace("/", "_").\
        replace("-", "_").replace("-", "_").replace("'", "").replace("\"", "").\
        replace("(", "").replace(")", "")


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

    return num_dice.isdecimal() and size_dice.isdecimal() and flat_bonus.isdecimal()

