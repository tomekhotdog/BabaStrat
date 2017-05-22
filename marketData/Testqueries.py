import unittest
from marketData.queries import *


class Testqueries(unittest.TestCase):

    def test_get_start_date(self):
        expected_date = datetime(2015, 5, 22)

        self.assertEqual(expected_date, get_start_date(DAY, datetime(2015, 5, 23)))
        self.assertEqual(expected_date, get_start_date(WEEK, datetime(2015, 5, 29)))
        self.assertEqual(expected_date, get_start_date(MONTH, datetime(2015, 6, 21)))
        self.assertEqual(expected_date, get_start_date(YEAR, datetime(2016, 5, 21)))
        self.assertEqual(expected_date, get_start_date(THREE_YEARS, datetime(2018, 5, 21)))

    def test_queryset_to_json(self):
        # TODO: create fake query set and use converter
        self.assertTrue(True)
