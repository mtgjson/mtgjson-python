from typing import Set

from bs4 import Tag

from mtgjson4.globals import COLORS, get_symbol_short_name, Color


def replace_symbol_images_with_tokens(tag: Tag) -> Set[Color]:
    """
    Replaces the img tags of symbols with token representations
    :rtype: set
    :return: The color symbols found
    """
    colors_found: Set[Color] = set()
    images = tag.find_all('img')
    for symbol in images:
        symbol_value = symbol['alt']
        symbol_mapped = get_symbol_short_name(symbol_value)
        symbol.replace_with(f'{{{symbol_mapped}}}')
        if symbol_mapped in COLORS:
            colors_found.add(symbol_mapped)

    return colors_found
