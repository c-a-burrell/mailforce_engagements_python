from unittest import TestCase

from date_utils import to_simple_date_string


class TestDateUtils(TestCase):
    def test_get_date_string(self):
        date_string = '2023-11-15T18:55:34.000Z'
        date_as_string = to_simple_date_string(date_string)
        self.assertEquals('2023-11-15 18:55', date_as_string)