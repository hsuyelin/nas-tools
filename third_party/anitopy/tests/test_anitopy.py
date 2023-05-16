# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

import anitopy
from tests.fixtures.failing_table import failing_table
from tests.fixtures.table import table


class TestAnitopy(TestCase):
    def parse_options(self, entry_options):
        if entry_options is None:
            return {}

        options = {}
        for option, value in entry_options.items():
            option_name = option.split('option_')[1]
            options[option_name] = value
        return options

    def test_table(self):
        for index, entry in enumerate(table):
            filename = entry[0]
            options = self.parse_options(entry[1])

            elements = anitopy.parse(filename, options=options)

            expected = dict(entry[2])
            if 'id' in expected.keys():
                del expected['id']
            self.assertEqual(expected, elements, 'on entry number %d' % index)

    def test_fails(self):
        failed = 0
        working_tests = []
        for index, entry in enumerate(failing_table):
            filename = entry[0]
            options = self.parse_options(entry[1])

            try:
                print('Index %d "%s"' % (index, filename))
            except:  # noqa: E722
                print(('Index %d "%s"' % (index, filename)).encode("utf-8"))

            elements = anitopy.parse(filename, options=options)

            expected = dict(entry[2])
            if 'id' in expected.keys():
                del expected['id']
            try:
                self.assertEqual(expected, elements)
                working_tests.append(index)
            except AssertionError as err:
                failed += 1
                print(err)
                print('----------------------------------------------------------------------')  # noqa E501

        print('\nFailed %d of %d failing cases tests' % (
            failed, len(failing_table)))
        if working_tests:
            print('There are {} working tests from the failing cases: {}'
                  .format(len(working_tests), working_tests))
