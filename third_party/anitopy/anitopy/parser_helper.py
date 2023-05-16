# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re
import unicodedata as ud

from anitopy.element import ElementCategory
from anitopy.token import TokenCategory, TokenFlags

DASHES = '-\u2010\u2011\u2012\u2013\u2014\u2015'


def find_number_in_string(string):
    is_number = [char.isdigit() for char in string]
    if any(is_number):
        return is_number.index(True)
    return None


def find_non_number_in_string(string):
    is_number = [char.isdigit() for char in string]
    if not all(is_number):
        return is_number.index(False)
    return None


def is_hexadecimal_string(string):
    return all([char in '1234567890abcdefABCDEF' for char in string])


def get_number_from_ordinal(string):
    ordinals = {
        '1st': '1', 'First': '1',
        '2nd': '2', 'Second': '2',
        '3rd': '3', 'Third': '3',
        '4th': '4', 'Fourth': '4',
        '5th': '5', 'Fifth': '5',
        '6th': '6', 'Sixth': '6',
        '7th': '7', 'Seventh': '7',
        '8th': '8', 'Eighth': '8',
        '9th': '9', 'Ninth': '9'
    }
    return ordinals.get(string, None)


def is_crc32(string):
    return len(string) == 8 and is_hexadecimal_string(string)


def is_dash_character(string):
    if len(string) != 1:
        return False
    return string in DASHES


def is_latin_char(char):
    return is_latin_char.cache.setdefault(char, 'LATIN' in ud.name(char))
is_latin_char.cache = {}  # noqa: E305


def is_mostly_latin_string(string):
    if len(string) == 0:
        return False
    latin_length = len([char for char in string if is_latin_char(char)])
    return latin_length / len(string) >= 0.5


def is_resolution(string):
    pattern = '\\d{3,4}([pP]|([xX\u00D7]\\d{3,4}))$|^[248]K$'
    return bool(re.match(pattern, string))


def check_anime_season_keyword(elements, parsed_tokens, token):
    def set_anime_season(first, second, content):
        elements.insert(ElementCategory.ANIME_SEASON, content)
        first.category = TokenCategory.IDENTIFIER
        second.category = TokenCategory.IDENTIFIER

    previous_token = parsed_tokens.find_previous(token, TokenFlags.NOT_DELIMITER)
    if previous_token:
        number = get_number_from_ordinal(previous_token.content)
        if number:
            set_anime_season(previous_token, token, number)
            return True

    next_token = parsed_tokens.find_next(token, TokenFlags.NOT_DELIMITER)
    if next_token and next_token.content.isdigit():
        set_anime_season(token, next_token, next_token.content)
        return True

    return False


def is_token_isolated(parsed_tokens, token):
    previous_token = parsed_tokens.find_previous(token, TokenFlags.NOT_DELIMITER)
    if previous_token.category != TokenCategory.BRACKET:
        return False

    next_token = parsed_tokens.find_next(token, TokenFlags.NOT_DELIMITER)
    if next_token is not None and next_token.category != TokenCategory.BRACKET:
        return False

    return True

###############################################################################


def build_element(elements, parsed_tokens, category, token_begin=None, token_end=None,
                  keep_delimiters=False):
    element = ''

    for token in parsed_tokens.get_list(begin=token_begin, end=token_end):
        if token.category == TokenCategory.UNKNOWN:
            element += token.content
            token.category = TokenCategory.IDENTIFIER
        elif token.category == TokenCategory.BRACKET:
            element += token.content
        elif token.category == TokenCategory.DELIMITER:
            delimiter = token.content
            if keep_delimiters:
                element += delimiter
            elif token != token_begin and token != token_end:
                if delimiter == ',' or delimiter == '&':
                    element += delimiter
                else:
                    element += ' '

    if not keep_delimiters:
        element = element.strip(' ' + DASHES)

    if element:
        elements.insert(category, element)
