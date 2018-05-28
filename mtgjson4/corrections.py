import re
import itertools
from typing import List, Dict, Union, Any
from mtgjson4.mtg_global import CardDescription

ReplacementType = Dict[str, Union[str, List[str], Any]]

def apply_corrections(match_replace_rules, cards_dictionary: List[CardDescription]) -> None:
    for replacement_rule in match_replace_rules:

        if isinstance(replacement_rule, dict):
            if replacement_rule.get('match'):
                apply_match(replacement_rule, cards_dictionary)
                continue
        elif isinstance(replacement_rule, str):
            if replacement_rule == 'noBasicLandWatermarks':
                no_basic_land_watermarks(cards_dictionary)
                continue
        # raise KeyError(replacement_rule)

def apply_match(replacement_rule, cards_dictionary: List[CardDescription]) -> None:
    keys = set(replacement_rule.keys())
    cards_to_modify = parse_match(replacement_rule['match'], cards_dictionary)
    keys.remove('match')

    if 'replace' in replacement_rule.keys():
        replace(replacement_rule['replace'], cards_to_modify)
        keys.remove('replace')

    if 'fixForeignNames' in replacement_rule.keys():
        fix_foreign_names(replacement_rule['fixForeignNames'], cards_to_modify)
        keys.remove('fixForeignNames')

    if 'fixFlavorNewlines' in replacement_rule.keys() and replacement_rule['fixFlavorNewlines']:
        fix_flavor_newlines(cards_to_modify)
        keys.remove('fixFlavorNewlines')

    # if keys:
    #     raise KeyError(keys)

def no_basic_land_watermarks(cards_dictionary):
    # TODO: Not sure what to do with this.
    pass

def replace(replacements: Dict[str, Any], cards_to_modify: List[CardDescription]) -> None:
    for key_name, replacement in replacements.items():
        for card in cards_to_modify:
            card[key_name] = replacement # type: ignore

def fix_foreign_names(replacements: List[Dict[str, Any]], cards_to_modify: List[CardDescription]) -> None:
    for lang_replacements in replacements:
        language_name = lang_replacements['language']
        new_name = lang_replacements['name']

        for card in cards_to_modify:
            for foreign_names_field in card['foreignNames']:
                if foreign_names_field['language'] == language_name:
                    foreign_names_field['name'] = new_name

def fix_flavor_newlines(cards_to_modify: List[CardDescription]) -> None:
    # The javascript version had the following regex to normalize em-dashes /(\s|")-\s*([^"—-]+)\s*$/
    for card in cards_to_modify:
        flavor = card.get('flavor')
        if flavor:
            # Ensure two quotes appear before the last em-dash
            # TODO
            pass


def parse_match(match_rule: Union[str, Dict[str, str]],
                card_list: List[CardDescription]
               ) -> List[CardDescription]:
    if isinstance(match_rule, list):
        return itertools.chain([parse_match(rule, card_list) for rule in match_rule])
    elif isinstance(match_rule, str):
        if match_rule == "*":
            return card_list
    elif isinstance(match_rule, dict):
        if len(match_rule.items()) != 1:
            raise KeyError(match_rule)
        for key, value in match_rule.items():
            if isinstance(value, list):
                return [card for card in card_list if key in card.keys() and card[key] in value]
            elif isinstance(value, (int, str)):
                return [card for card in card_list if card.get(key) == value]
    raise KeyError(match_rule)
