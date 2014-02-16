# -*- coding: UTF-8 -*-

import unittest
from models.history import History

class HistoryTest(unittest.TestCase):
    def testConstructor(self):
        history = History(5)
        self.assertEquals([], history.get_log())
        history.add_log(['1', '2', '3', '4', '5'])
        self.assertEquals(['1', '2', '3', '4', '5'], history.get_log())

    def testHistoryLengthAndMovement(self):
        history = History(2)
        history.add_log(['1', '2', '3', '4'])
        # we only the last 2 one
        self.assertEqual(['3', '4'], history.get_log())
        history.increase_cursor()
        # if we want to the next line do nothing
        self.assertEquals(['3', '4'], history.get_log())
        history.decrease_cursor()
        self.assertEquals(['2', '3'], history.get_log())
        # the increase work
        history.increase_cursor()
        self.assertEquals(['3', '4'], history.get_log())
        history.go_to_the_top()
        self.assertEquals(['1', '2'], history.get_log())

    def testHistoryLengthOnlyOneData(self):
        history = History(2)
        history.add_log(['1'])
        # if only one entry you can do more or less nothing..
        self.assertEqual(['1'], history.get_log())
        history.increase_cursor()
        self.assertEquals(['1'], history.get_log())
        history.decrease_cursor()
        self.assertEquals(['1'], history.get_log())
        history.increase_cursor()
        self.assertEquals(['1'], history.get_log())
        history.go_to_the_top()
        self.assertEquals(['1'], history.get_log())

