import unittest
from enum import Enum

from finra.enum_converter import EnumConverter

from .common import no_duplicates


# A few test to complete coverage. Most code paths tested by child classes.
class TestEnumConverter(unittest.TestCase):
    
    @no_duplicates
    def test_type_error_non_string_value(self):
        with self.assertRaisesRegex(TypeError, 'enum.Enum'):
            EnumConverter(False)._type_error(123, Enum)


if __name__ == "__main__": # pragma: no cover
    unittest.main()
