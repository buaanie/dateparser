import itertools

from datetime import datetime
from tests import BaseTestCase
from nose_parameterized import parameterized, param
from dateparser.utils import (
    find_date_separator, localize_timezone, apply_timezone,
    apply_timezone_from_settings, registry, increase_regex_replacements_group_positions
)
from pytz import UnknownTimeZoneError, utc
from dateparser.conf import settings


class TestUtils(BaseTestCase):
    def setUp(self):
        super(TestUtils, self).setUp()
        self.date_format = None
        self.result = None

    def given_date_format(self, date_format):
        self.date_format = date_format

    def when_date_seperator_is_parsed(self):
        self.result = find_date_separator(self.date_format)

    def then_date_seperator_is(self, sep):
        self.assertEqual(self.result, sep)

    @staticmethod
    def make_class_without_get_keys():
        class SomeClass:
            pass
        some_class = SomeClass
        return some_class

    @parameterized.expand([
        param(date_format=fmt.format(sep=sep), expected_sep=sep)
        for (fmt, sep) in itertools.product(
            ['%d{sep}%m{sep}%Y', '%d{sep}%m{sep}%Y %H:%M'],
            ['/', '.', '-', ':'])
    ])
    def test_separator_extraction(self, date_format, expected_sep):
        self.given_date_format(date_format)
        self.when_date_seperator_is_parsed()
        self.then_date_seperator_is(expected_sep)

    @parameterized.expand([
        param(datetime(2015, 12, 12), timezone='UTC', zone='UTC'),
        param(datetime(2015, 12, 12), timezone='Asia/Karachi', zone='Asia/Karachi'),
        param(datetime(2015, 12, 12, tzinfo=utc), timezone='UTC', zone='UTC'),
    ])
    def test_localize_timezone_function(self, date, timezone, zone):
        tzaware_dt = localize_timezone(date, timezone)
        self.assertEqual(tzaware_dt.tzinfo.zone, zone)

    @parameterized.expand([
        param(datetime(2015, 12, 12), timezone='UTB'),
        param(datetime(2015, 12, 12), timezone='Asia/Karach'),
    ])
    def test_localize_timezone_function_raise_error(self, date, timezone):
        self.assertRaises(UnknownTimeZoneError, localize_timezone, date, timezone)

    @parameterized.expand([
        param(datetime(2015, 12, 12), timezone='UTC+3', zone='UTC\+03:00'),
    ])
    def test_localize_timezone_function_exception(self, date, timezone, zone):
        tzaware_dt = localize_timezone(date, timezone)
        self.assertEqual(tzaware_dt.tzinfo._StaticTzInfo__name, zone)

    @parameterized.expand([
        param(datetime(2015, 12, 12, 10, 12), timezone='Asia/Karachi', expected=datetime(2015, 12, 12, 15, 12)),
        param(datetime(2015, 12, 12, 10, 12), timezone='-0500', expected=datetime(2015, 12, 12, 5, 12)),
    ])
    def test_apply_timezone_function(self, date, timezone, expected):
        result = apply_timezone(date, timezone)
        result = result.replace(tzinfo=None)
        self.assertEqual(expected, result)

    @parameterized.expand([
        param(datetime(2015, 12, 12, 10, 12), timezone='Asia/Karachi', expected=datetime(2015, 12, 12, 15, 12)),
        param(datetime(2015, 12, 12, 10, 12), timezone='-0500', expected=datetime(2015, 12, 12, 5, 12)),
    ])
    def test_apply_timezone_from_settings_function(self, date, timezone, expected):
        result = apply_timezone_from_settings(date, settings.replace(**{'TO_TIMEZONE': timezone, 'TIMEZONE': 'UTC'}))
        self.assertEqual(expected, result)

    @parameterized.expand([
        param(datetime(2015, 12, 12, 10, 12),
              expected=datetime(2015, 12, 12, 10, 12)),

    ])
    def test_apply_timezone_from_settings_function_none_settings(self, date, expected):
        result = apply_timezone_from_settings(date, None)
        self.assertEqual(expected, result)

    @parameterized.expand([
        param(datetime(2015, 12, 12, 10, 12),),
        param(datetime(2015, 12, 12, 10, 12),),
    ])
    def test_apply_timezone_from_settings_function_should_return_tz(self, date):
        result = apply_timezone_from_settings(date, settings.replace(**{'RETURN_AS_TIMEZONE_AWARE': True}))
        self.assertTrue(bool(result.tzinfo))

    def test_registry_when_get_keys_not_implemented(self):
        cl = self.make_class_without_get_keys()
        self.assertRaises(NotImplementedError, registry, cl)

    @parameterized.expand([
        param(r'\1\g<2>text', 1, r'\2\g<3>text'),
    ])
    def test_increase_regex_replacements_group_positions(self, repl, incr, expected):
        result = increase_regex_replacements_group_positions(repl, incr)
        self.assertTrue(result, expected)

