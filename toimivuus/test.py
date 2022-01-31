import os
import unittest
from unittest import mock
from toimivuus import EventType
from toimivuus import RawHfpFile
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

    @mock.patch.dict(os.environ, {'DATA_CACHE_DIRECTORY': 'tmp'})
    def test_rawhfpfile_not_exists_locally_error(self):
        """Knows that raw file of given base name does not exist locally."""
        rhf = RawHfpFile(base_name='2020-01-01T01', event_type=EventType.ARR)
        self.assertFalse(rhf.local_exists())

    @mock.patch.dict(os.environ, {'DATA_CACHE_DIRECTORY': 'tmp'})
    def test_rawhfpdump_creation(self):
        """Can create a simple RawHfpDump."""
        self.assertIsInstance(
            RawHfpDump(
                first_datehour = '2020-01-02T03',
                last_datehour = '2020-01-02T06',
                event_types = ['VP', 'DOO', 'DOC']
            ),
            RawHfpDump
        )
        
    @mock.patch.dict(os.environ, {'DATA_CACHE_DIRECTORY': 'tmp'})
    def test_rawhfpdump_creation_without_last_datehour(self):
        """Can create a simple RawHfpDump."""
        self.assertIsInstance(
            RawHfpDump(
                first_datehour = '2020-01-02T03',
                last_datehour = None,
                event_types = ['VP', 'DOO', 'DOC']
            ),
            RawHfpDump
        )

    @mock.patch.dict(os.environ, {'DATA_CACHE_DIRECTORY': 'tmp'})
    def test_rawhfpdump_base_name(self):
        """RawHfpDump has the desired base name."""
        self.assertEqual(
            RawHfpDump(
                first_datehour = '2020-01-02T03',
                last_datehour = '2020-01-02T06',
                event_types = ['VP', 'DOO', 'DOC']
            ).base_name,
            '2020-01-02T03_2020-01-02T06'
        )

    @mock.patch.dict(os.environ, {'DATA_CACHE_DIRECTORY': 'tmp'})
    def test_rawhfpdump_datetime_error(self):
        """Poorly formatted datetime throws an error."""
        with self.assertRaises(ValueError):
            RawHfpDump(
                first_datehour = '2020010203',
                last_datehour = '2020-01-02T06',
                event_types = ['VP', 'DOO', 'DOC']
            )

if __name__ == '__main__':
    unittest.main()