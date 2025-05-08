import unittest
from unittest.mock import Mock
from app.native_functions import NativeClock


class TestNativeFunctions(unittest.TestCase):
    def test_native_clock_arity(self):
        """Test that the clock function reports correct arity (0 arguments)."""
        clock = NativeClock()
        self.assertEqual(clock.arity(), 0)

    def test_native_clock_call(self):
        """Test that calling clock returns a float value representing time."""
        clock = NativeClock()
        interpreter = Mock()  # Mock interpreter, not used in clock function
        result = clock(interpreter, [])
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_native_clock_str(self):
        """Test the string representation of the native clock function."""
        clock = NativeClock()
        self.assertEqual(str(clock), "<native fn>")


if __name__ == '__main__':
    unittest.main()
