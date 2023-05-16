# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from enum import Enum


class TokenCategory(Enum):
    # Auto enumerate elements
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    UNKNOWN = ()
    BRACKET = ()
    DELIMITER = ()
    IDENTIFIER = ()
    INVALID = ()


class TokenFlags:
    NONE = 0
    # Categories
    BRACKET = 1 << 0
    NOT_BRACKET = 1 << 1
    DELIMITER = 1 << 2
    NOT_DELIMITER = 1 << 3
    IDENTIFIER = 1 << 4
    NOT_IDENTIFIER = 1 << 5
    UNKNOWN = 1 << 6
    NOT_UNKNOWN = 1 << 7
    VALID = 1 << 8
    NOT_VALID = 1 << 9
    # Enclosed
    ENCLOSED = 1 << 10
    NOT_ENCLOSED = 1 << 11
    # Masks
    MASK_CATEGORIES = \
        BRACKET | NOT_BRACKET | \
        DELIMITER | NOT_DELIMITER | \
        IDENTIFIER | NOT_IDENTIFIER | \
        UNKNOWN | NOT_UNKNOWN | \
        VALID | NOT_VALID
    MASK_ENCLOSED = ENCLOSED | NOT_ENCLOSED


class Token:
    def __init__(self, category=TokenCategory.UNKNOWN, content=None,
                 enclosed=False):
        self.category = category
        self.content = content
        self.enclosed = enclosed

    def __repr__(self):
        return 'Token(category = {0}, content = "{1}", enclosed = {2}'.format(
            self.category, self.content, self.enclosed
        )

    def check_flags(self, flags):
        def check_flag(flag):
            return (flags & flag) == flag

        if flags & TokenFlags.MASK_ENCLOSED:
            success = self.enclosed if check_flag(TokenFlags.ENCLOSED) \
                else not self.enclosed
            if not success:
                return False

        if flags & TokenFlags.MASK_CATEGORIES:
            def check_category(fe, fn, cat):
                return self.category == cat if check_flag(fe) else \
                       self.category != cat if check_flag(fn) else False
            if check_category(TokenFlags.BRACKET, TokenFlags.NOT_BRACKET,
                              TokenCategory.BRACKET):
                return True
            if check_category(TokenFlags.DELIMITER, TokenFlags.NOT_DELIMITER,
                              TokenCategory.DELIMITER):
                return True
            if check_category(TokenFlags.IDENTIFIER, TokenFlags.NOT_IDENTIFIER,
                              TokenCategory.IDENTIFIER):
                return True
            if check_category(TokenFlags.UNKNOWN, TokenFlags.NOT_UNKNOWN,
                              TokenCategory.UNKNOWN):
                return True
            if check_category(TokenFlags.NOT_VALID, TokenFlags.VALID,
                              TokenCategory.INVALID):
                return True
            return False

        return True


class Tokens:
    def __init__(self):
        self._tokens = []

    def empty(self):
        return len(self._tokens) == 0

    def append(self, token):
        self._tokens.append(token)

    def insert(self, index, token):
        self._tokens.insert(index, token)

    def update(self, tokens):
        self._tokens = tokens

    def get(self, index):
        return self._tokens[index]

    def get_list(self, flags=None, begin=None, end=None):
        tokens = self._tokens
        begin_index = 0 if begin is None else self.get_index(begin)
        end_index = len(tokens) if end is None else self.get_index(end)
        if flags is None:
            return tokens[begin_index:end_index+1]
        else:
            return [token for token in tokens[begin_index:end_index+1]
                    if token.check_flags(flags)]

    def get_index(self, token):
        return self._tokens.index(token)

    def distance(self, token_begin, token_end):
        begin_index = 0 if token_begin is None else self.get_index(token_begin)
        end_index = len(self._tokens) if token_end is None else \
            self.get_index(token_end)
        return end_index - begin_index

    @staticmethod
    def _find_in_tokens(tokens, flags):
        for token in tokens:
            if token.check_flags(flags):
                return token
        return None

    def find(self, flags):
        return self._find_in_tokens(self._tokens, flags)

    def find_previous(self, token, flags):
        tokens = self._tokens
        if token is None:
            tokens = tokens[::-1]
        else:
            token_index = self.get_index(token)
            tokens = tokens[token_index-1::-1]
        return self._find_in_tokens(tokens, flags)

    def find_next(self, token, flags):
        tokens = self._tokens
        if token is not None:
            token_index = self.get_index(token)
            tokens = tokens[token_index+1:]
        return self._find_in_tokens(tokens, flags)
