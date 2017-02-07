import unittest
import datetime
from context import smcAPI

utils = smcAPI.utils

class TestUtils (unittest.TestCase):
    def test_detect_types(self):
        types = {
            1: 'Sun, 30th October to Thu, 3rd November',
            2: 'Wed, 7th September to Fri, 9th September 9:00am to 4:00pm',
            3: 'Tue, 1st November',
            4: 'Tue, 25th October 6:00pm',
            5: 'Wed, 2nd November 10:30am to 11:30am'
        }
        for type_ in types:
            with self.subTest(type_=type_):
                self.assertEqual(utils.internal.detect_date_type(types[type_]), type_)
    def test_parse_types_no_assumptions(self):
        types = {
            1: (
                'Sun, 30th October to Thu, 3rd November',
                (
                    datetime.datetime(2015, 10, 30, 0, 0),
                    datetime.datetime(2015, 11, 30, 23, 59)
                )
                ),
            2: (
                'Wed, 7th September to Fri, 9th September 9:00am to 4:00pm',
                (
                    datetime.datetime(2015, 9, 7, 9, 0),
                    datetime.datetime(2015, 9, 9, 16, 0)
                )
                ),
            3: (
                'Tue, 1st November',
                (
                    datetime.datetime(2015, 11, 1, 0, 0),
                    datetime.datetime(2015, 11, 1, 23, 59)
                )
                ),
            4: (
                'Tue, 25th October 6:00pm',
                (
                    datetime.datetime(2015, 10, 25, 18, 0),
                     datetime.datetime(2015, 10, 25, 23, 59)
                )
                ),
            5: (
                'Wed, 2nd November 10:30am to 11:30am',
                (
                    datetime.datetime(2015, 11, 2, 10, 30),
                    datetime.datetime(2015, 11, 2, 11, 30)
                )
                )
        }
        for type_ in types:
            with self.subTest(type_=type_):
                start, end = utils.internal.parse_date(types[type_][0], 2015, False)
                self.assertEqual(start, types[type_][1][0])
                self.assertEqual(end, types[type_][1][1])

unittest.main()
