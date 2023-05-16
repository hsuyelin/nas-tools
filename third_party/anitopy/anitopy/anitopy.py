# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from anitopy.element import Elements, ElementCategory
from anitopy.keyword import keyword_manager
from anitopy.parser import Parser
from anitopy.token import Tokens
from anitopy.tokenizer import Tokenizer


default_options = {
    'allowed_delimiters': ' _.&+,|',
    'ignored_strings': [],
    'parse_episode_number': True,
    'parse_episode_title': True,
    'parse_file_extension': True,
    'parse_release_group': True
}


def parse(filename, options=default_options):
    elements = Elements()
    tokens = Tokens()

    # Add missing options
    for key, value in default_options.items():
        options.setdefault(key, value)

    elements.insert(ElementCategory.FILE_NAME, filename)
    if options['parse_file_extension']:
        filename, extension = remove_extension_from_filename(filename)
        if extension:
            elements.insert(ElementCategory.FILE_EXTENSION, extension)

    if options['ignored_strings']:
        filename = remove_ignored_strings_from_filename(
            filename, options['ignored_strings'])

    if not filename:
        return None

    tokenizer = Tokenizer(filename, options, elements, tokens)
    if not tokenizer.tokenize():
        return None

    parser = Parser(options, elements, tokens)
    if not parser.parse():
        return None

    return elements.get_dictionary()


def remove_extension_from_filename(filename):
    split_filename = filename.rsplit('.', 1)

    if len(split_filename) < 2:
        return filename, None

    new_filename, extension = split_filename

    max_length = 4
    if len(extension) > max_length:
        return filename, None

    if not extension.isalnum():
        return filename, None

    keyword = keyword_manager.normalize(extension)
    if not keyword_manager.find(keyword, ElementCategory.FILE_EXTENSION):
        return filename, None

    return new_filename, extension


def remove_ignored_strings_from_filename(filename, ignored_strings):
    for string in ignored_strings:
        filename = filename.replace(string, '')
    return filename
