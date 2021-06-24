import math


def hex2rgba_palette(hex_list):
    """
    Convert a list of hex colors to a list of rgba colors.
    """
    mapper = lambda c: (*hex_to_rgb(c["value"]), 255)
    return [mapper(c) for c in hex_list]


def hex_to_rgb(hex_num: str):
    """
    Convert hex_num to a (R, G, B) tuple containing color components represented\
    by integers between 0 and 255.
    :param hex_num: A hex color string with no leading #
    """
    return tuple(int(hex_num[i : i + 2], 16) for i in (0, 2, 4))


def cooldown(num_users: int):
    """Get the cooldown when num_users users are online."""
    return 2.5 * math.sqrt(num_users + 11.96) + 6.5
