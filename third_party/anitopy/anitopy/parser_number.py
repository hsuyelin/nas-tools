# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re

from anitopy import parser_helper
from anitopy.element import ElementCategory
from anitopy.keyword import keyword_manager
from anitopy.token import TokenCategory, TokenFlags, Token

ANIME_YEAR_MIN = 1900
ANIME_YEAR_MAX = 2050
EPISODE_NUMBER_MAX = ANIME_YEAR_MIN - 1
VOLUME_NUMBER_MAX = 20


def str2int(string):
    try:
        return int(string)
    except ValueError:
        return 0


def is_valid_episode_number(number):
    return str2int(number) <= EPISODE_NUMBER_MAX


def set_episode_number(elements, number, token, validate):
    if validate and not is_valid_episode_number(number):
        return False

    token.category = TokenCategory.IDENTIFIER

    category = ElementCategory.EPISODE_NUMBER

    # Handle equivalent numbers
    if elements.get_check_alt_number():
        # TODO: check if getting only the first episode number is enough
        episode_number = elements.get(ElementCategory.EPISODE_NUMBER)[0]
        if str2int(number) > str2int(episode_number):
            category = ElementCategory.EPISODE_NUMBER_ALT
        elif str2int(number) < str2int(episode_number):
            elements.remove(ElementCategory.EPISODE_NUMBER, episode_number)
            elements.insert(ElementCategory.EPISODE_NUMBER_ALT, episode_number)
        else:
            return False

    elements.insert(category, number)
    return True


def set_alternative_episode_number(elements, number, token):
    elements.insert(ElementCategory.EPISODE_NUMBER_ALT, number)
    token.category = TokenCategory.IDENTIFIER

    return True


def check_extent_keyword(elements, parsed_tokens, category, token):
    next_token = parsed_tokens.find_next(token, TokenFlags.NOT_DELIMITER)

    if next_token.category == TokenCategory.UNKNOWN:
        if next_token and \
                parser_helper.find_number_in_string(next_token.content) \
                is not None:
            if category == ElementCategory.EPISODE_NUMBER:
                if not match_episode_patterns(
                        elements, parsed_tokens, next_token.content, next_token):
                    set_episode_number(
                        elements, next_token.content, next_token, validate=False)
            elif category == ElementCategory.VOLUME_NUMBER:
                if not match_volume_patterns(
                        elements, next_token.content, next_token):
                    set_volume_number(
                        elements, next_token.content, next_token, validate=False)
            else:
                return False
            token.category = TokenCategory.IDENTIFIER
            return True

    return False

###############################################################################


def number_comes_after_prefix(elements, parsed_tokens, category, token):
    number_begin = parser_helper.find_number_in_string(token.content)
    prefix = token.content[:number_begin]

    keyword = keyword_manager.find(keyword_manager.normalize(prefix), category)
    if keyword:
        number = token.content[number_begin:]
        if category == ElementCategory.EPISODE_PREFIX:
            if match_episode_patterns(elements, parsed_tokens, number, token):
                return True
            return set_episode_number(elements, number, token, validate=False)
        if category == ElementCategory.VOLUME_PREFIX:
            if match_volume_patterns(elements, number, token):
                return True
            return set_volume_number(elements, number, token, validate=False)
        if category == ElementCategory.ANIME_SEASON_PREFIX:
            return set_season_number(elements, number, token)

    return False


def number_comes_before_another_number(elements, parsed_tokens, token):
    separator_token = parsed_tokens.find_next(token, TokenFlags.NOT_DELIMITER)

    if separator_token:
        separator = separator_token.content
        if separator == '&' or separator == 'of':
            other_token = parsed_tokens.find_next(
                separator_token, TokenFlags.NOT_DELIMITER)
            if other_token and other_token.content.isdigit():
                set_episode_number(elements, token.content, token, validate=False)
                if separator == '&':
                    set_episode_number(
                        elements, other_token.content, token, validate=False)
                separator_token.category = TokenCategory.IDENTIFIER
                other_token.category = TokenCategory.IDENTIFIER
                return True

    return False


def search_for_episode_patterns(elements, parsed_tokens, tokens):
    for token in tokens:
        numeric_front = token.content[0].isdigit()

        if not numeric_front:
            # e.g. "EP.1", "Vol.1"
            if number_comes_after_prefix(
                    elements, parsed_tokens, ElementCategory.EPISODE_PREFIX, token):
                return True
            if number_comes_after_prefix(
                    elements, parsed_tokens, ElementCategory.VOLUME_PREFIX, token):
                continue
            if number_comes_after_prefix(
                    elements, parsed_tokens, ElementCategory.ANIME_SEASON_PREFIX, token):
                continue
        else:
            # e.g. "8 & 10", "01 of 24"
            if number_comes_before_another_number(elements, parsed_tokens, token):
                return True
        # Look for other patterns
        if match_episode_patterns(elements, parsed_tokens, token.content, token):
            return True

    return False

###############################################################################


def match_single_episode_pattern(elements, word, token):
    pattern = '(\\d{1,4})[vV](\\d)$'
    match = re.match(pattern, word)
    if match:
        set_episode_number(elements, match.group(1), token, validate=False)
        elements.insert(ElementCategory.RELEASE_VERSION, match.group(2))
        return True

    return False


def match_multi_episode_pattern(elements, word, token):
    pattern = '(\\d{1,4})(?:[vV](\\d))?[-~&+](\\d{1,4})(?:[vV](\\d))?$'
    match = re.match(pattern, word)
    if match:
        lower_bound = match.group(1)
        upper_bound = match.group(3)
        # Avoid matching expressions such as "009-1" or "5-2"
        if int(lower_bound) < int(upper_bound):
            if set_episode_number(elements, lower_bound, token, validate=True):
                set_episode_number(elements, upper_bound, token, validate=False)
                if match.group(2):
                    elements.insert(
                        ElementCategory.RELEASE_VERSION, match.group(2))
                if match.group(4):
                    elements.insert(
                        ElementCategory.RELEASE_VERSION, match.group(4))
                return True

    return False


def match_season_and_episode_pattern(elements, word, token):
    pattern = 'S?(\\d{1,2})(?:-S?(\\d{1,2}))?' +\
              '(?:x|[ ._-x]?E)(\\d{1,4})(?:-E?(\\d{1,4}))?' +\
              '(?:[vV](\\d))?$'
    match = re.match(pattern, word, flags=re.IGNORECASE)

    if match:
        if int(match.group(1)) == 0:
            return False
        elements.insert(ElementCategory.ANIME_SEASON, match.group(1))
        if match.group(2):
            elements.insert(ElementCategory.ANIME_SEASON, match.group(2))
        set_episode_number(elements, match.group(3), token, validate=False)
        if match.group(4):
            set_episode_number(elements, match.group(4), token, validate=False)
        if match.group(5):
            elements.insert(ElementCategory.RELEASE_VERSION, match.group(5))
        return True

    return False


def match_type_and_episode_pattern(elements, parsed_tokens, word, token):
    number_begin = parser_helper.find_number_in_string(word)
    prefix = word[:number_begin]

    keyword = keyword_manager.find(
        keyword_manager.normalize(prefix), ElementCategory.ANIME_TYPE)

    if keyword:
        elements.insert(ElementCategory.ANIME_TYPE, prefix)
        number = word[number_begin:]
        if match_episode_patterns(elements, parsed_tokens, number, token) or \
                set_episode_number(elements, number, token, validate=True):
            # Split token (we do this last in order to avoid invalidating our
            # token reference earlier)
            token_index = parsed_tokens.get_index(token)
            token.content = number
            parsed_tokens.insert(token_index, Token(
                TokenCategory.IDENTIFIER if keyword.options.identifiable
                else TokenCategory.UNKNOWN,
                prefix, token.enclosed))
            return True

    return False


def match_fractional_episode_pattern(elements, word, token):
    # We don't allow any fractional part other than ".5", because there are
    # cases where such a number is a part of the anime title (e.g. "Evangelion:
    # 1.11", "Tokyo Magnitude 8.0") or a keyword (e.g. "5.1").
    pattern = '\\d+\\.5$'
    match = re.match(pattern, word)
    if match:
        if set_episode_number(elements, word, token, validate=True):
            return True

    return False


def match_partial_episode_pattern(elements, word, token):
    non_number_begin = parser_helper.find_non_number_in_string(word)
    suffix = word[non_number_begin:]

    def is_valid_suffix(s):
        return len(s) == 1 and s in 'ABCabc'

    if is_valid_suffix(suffix):
        if set_episode_number(elements, word, token, validate=True):
            return True

    return False


def match_number_sign_pattern(elements, word, token):
    if word[0] != '#':
        return False

    pattern = '#(\\d{1,4})(?:[-~&+](\\d{1,4}))?(?:[vV](\\d))?$'
    match = re.match(pattern, word)

    if match:
        if set_episode_number(elements, match.group(1), token, validate=True):
            if match.group(2):
                set_episode_number(elements, match.group(2), token, validate=True)
            if match.group(3):
                elements.insert(ElementCategory.RELEASE_VERSION,
                                match.group(3))
            return True

    return False


def match_japanese_counter_pattern(elements, word, token):
    if word[-1] != '\u8A71':
        return False

    pattern = '(\\d{1,4})\u8A71$'
    match = re.match(pattern, word)

    if match:
        if set_episode_number(elements, match.group(1), token, validate=False):
            return True

    return False


def match_episode_patterns(elements, parsed_tokens, word, token):
    if word.isdigit():
        return False

    word = word.strip(' -')

    numeric_front = word[0].isdigit()
    numeric_back = word[-1].isdigit()

    # e.g. "01v2"
    if numeric_front and numeric_back:
        if match_single_episode_pattern(elements, word, token):
            return True
    # e.g. "01-02", "03-05v2"
    if numeric_front and numeric_back:
        if match_multi_episode_pattern(elements, word, token):
            return True
    # e.g. "2x01", "S01E03", "S01-02xE001-150", "S01E06v2"
    if numeric_back:
        if match_season_and_episode_pattern(elements, word, token):
            return True
    # e.g. "ED1", "OP4a", "OVA2"
    if not numeric_front:
        if match_type_and_episode_pattern(elements, parsed_tokens, word, token):
            return True
    # e.g. "07.5"
    if numeric_front and numeric_back:
        if match_fractional_episode_pattern(elements, word, token):
            return True
    # e.g. "4a", "111C"
    if numeric_front and not numeric_back:
        if match_partial_episode_pattern(elements, word, token):
            return True
    # e.g. "#01", "#02-03v2"
    if numeric_back:
        if match_number_sign_pattern(elements, word, token):
            return True
    # U+8A71 is used as counter for stories, episodes of TV series, etc.
    if numeric_front:
        if match_japanese_counter_pattern(elements, word, token):
            return True

    return False

###############################################################################


def is_valid_volume_number(number):
    return int(number) <= VOLUME_NUMBER_MAX


def set_volume_number(elements, number, token, validate):
    if validate:
        if not is_valid_volume_number(number):
            return False

    elements.insert(ElementCategory.VOLUME_NUMBER, number)
    token.category = TokenCategory.IDENTIFIER
    return True


def match_single_volume_pattern(elements, word, token):
    pattern = '(\\d{1,2})[vV](\\d)$'
    match = re.match(pattern, word)

    if match:
        set_volume_number(elements, match.group(1), token, validate=False)
        elements.insert(ElementCategory.RELEASE_VERSION, match.group(2))
        return True

    return False


def match_multi_volume_pattern(elements, word, token):
    pattern = '(\\d{1,2})[-~&+](\\d{1,2})(?:[vV](\\d))?$'
    match = re.match(pattern, word)

    if match:
        lower_bound = match.group(1)
        upper_bound = match.group(2)
        if int(lower_bound) < int(upper_bound):
            if set_volume_number(elements, lower_bound, token, validate=True):
                set_volume_number(elements, upper_bound, token, validate=False)
                if match.group(3):
                    elements.insert(ElementCategory.RELEASE_VERSION,
                                    match.group(3))
                return True

    return False


def match_volume_patterns(elements, word, token):
    # All patterns contain at least one non-numeric character
    if word.isdigit():
        return False

    word = word.strip(' -')

    numeric_front = word[0].isdigit()
    numeric_back = word[-1].isdigit()

    # e.g. "01v2"
    if numeric_front and numeric_back:
        if match_single_volume_pattern(elements, word, token):
            return True
    # e.g. "01-02", "03-05v2"
    if numeric_front and numeric_back:
        if match_multi_volume_pattern(elements, word, token):
            return True

    return False

###############################################################################


def set_season_number(elements, number, token):
    if not number.isdigit():
        return False

    elements.insert(ElementCategory.ANIME_SEASON, number)
    token.category = TokenCategory.IDENTIFIER
    return True

###############################################################################


def search_for_equivalent_numbers(elements, parsed_tokens, tokens):
    for token in tokens:
        if parser_helper.is_token_isolated(parsed_tokens, token) or \
                not is_valid_episode_number(token.content):
            continue

        # Find the first enclosed, non-delimiter token
        next_token = parsed_tokens.find_next(token, TokenFlags.NOT_DELIMITER)
        if next_token is None or next_token.category != TokenCategory.BRACKET:
            continue
        next_token = parsed_tokens.find_next(
            next_token, TokenFlags.ENCLOSED | TokenFlags.NOT_DELIMITER)
        if next_token is None or next_token.category != TokenCategory.UNKNOWN:
            continue

        # Check if it's an isolated number
        if not parser_helper.is_token_isolated(parsed_tokens, next_token) or \
                not next_token.content.isdigit() or \
                not is_valid_episode_number(next_token.content):
            continue

        episode = min(token, next_token, key=lambda t: int(t.content))
        alt_episode = max(token, next_token, key=lambda t: int(t.content))

        set_episode_number(elements, episode.content, episode, validate=False)
        set_alternative_episode_number(elements, alt_episode.content, alt_episode)

        return True

    return False


def search_for_separated_numbers(elements, parsed_tokens, tokens):
    for token in tokens:
        previous_token = parsed_tokens.find_previous(token, TokenFlags.NOT_DELIMITER)

        # See if the number has a preceding "-" separator
        if previous_token.category == TokenCategory.UNKNOWN and \
                parser_helper.is_dash_character(previous_token.content):
            if set_episode_number(elements, token.content, token, validate=True):
                previous_token.category = TokenCategory.IDENTIFIER
                return True

    return False


def search_for_isolated_numbers(elements, parsed_tokens, tokens):
    for token in tokens:
        if not token.enclosed or not parser_helper.is_token_isolated(parsed_tokens, token):
            continue

        if set_episode_number(elements, token.content, token, validate=True):
            return True

    return False


def search_for_last_number(elements, parsed_tokens, tokens):
    for token in tokens:
        token_index = parsed_tokens.get_index(token)

        # Assuming that episode number always comes after the title, first
        # token cannot be what we're looking for
        if token_index == 0:
            continue

        # An enclosed token is unlikely to be the episode number at this point
        if token.enclosed:
            continue

        # Ignore if it's the first non-enclosed, non-delimiter token
        if all([t.enclosed or t.category == TokenCategory.DELIMITER
                for t in parsed_tokens.get_list()[:token_index]]):
            continue

        # Ignore if the previous token is "Movie" or "Part"
        previous_token = parsed_tokens.find_previous(token, TokenFlags.NOT_DELIMITER)
        if previous_token.category == TokenCategory.UNKNOWN:
            if previous_token.content.lower() == 'movie' or \
                    previous_token.content.lower() == 'part':
                continue

        # We'll use this number after all
        if set_episode_number(elements, token.content, token, validate=True):
            return True

    return False
