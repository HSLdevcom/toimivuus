import unittest
from toimivuus import EventType
from toimivuus import RawHfpDump
from datetime import datetime

class TestAll(unittest.TestCase):
    # TODO: Separate later into manageable
    #       test classes, as the amount grows.
    
    def test_valid_event_types(self):
        """Can cast valid uppercase strings
        to EventType instances."""
        self.assertIsInstance(
            EventType['VP'], EventType
        )
        self.assertIsInstance(
            EventType['DOO'], EventType
        )
        self.assertIsInstance(
            EventType['VJOUT'], EventType
        )
    
    def test_lowercase_event_type_error(self):
        """Casting lowercase string to EventType
        throws an error."""
        with self.assertRaises(KeyError):
            EventType['vp']

    def test_invalid_event_type_error(self):
        """Casting a random string to EventType
        throws an error."""
        with self.assertRaises(KeyError):
            EventType['FOO']

    def test_rawhfpdump_creation(self):
        """Can create a simple RawHfpDump."""
        self.assertIsInstance(
            RawHfpDump(
                dump_datetime = datetime(2020, 1, 2, 3),
                event_types = ['VP', 'DOO', 'DOC']
            ),
            RawHfpDump
        )

    def test_rawhfpdump_base_name(self):
        """RawHfpDump has the desired base name."""
        self.assertEquals(
            RawHfpDump(
                dump_datetime = datetime(2020, 1, 2, 3),
                event_types = ['VP', 'DOO', 'DOC']
            ).base_name,
            '2020-01-02T03'
        )

    def test_rawhfpdump_datetime_error(self):
        """Non-datetime argument throws an error."""
        with self.assertRaises(AttributeError):
            RawHfpDump(
                dump_datetime = '2020010203',
                event_types = ['VP', 'DOO', 'DOC']
            )

if __name__ == '__main__':
    unittest.main()