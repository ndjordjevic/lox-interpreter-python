import os
import sys
import unittest
from io import StringIO

# Add the parent directory of 'tests' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanner import Scanner
from app.token_type import TokenType
from app.utils import error_state


class TestScanner(unittest.TestCase):
    def setUp(self):
        error_state["had_error"] = False

    def test_single_character_tokens(self):
        source = "(){}.,-+;*"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.RIGHT_BRACE,
            TokenType.DOT,
            TokenType.COMMA,
            TokenType.MINUS,
            TokenType.PLUS,
            TokenType.SEMICOLON,
            TokenType.STAR,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_string_token(self):
        source = '"hello world"'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "hello world")
        self.assertEqual(tokens[1].type, TokenType.EOF)

    def test_number_token(self):
        source = "123 45.67"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 123)
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].literal, 45.67)
        self.assertEqual(tokens[2].type, TokenType.EOF)

    def test_identifier_token(self):
        source = "var if else"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.VAR)
        self.assertEqual(tokens[1].type, TokenType.IF)
        self.assertEqual(tokens[2].type, TokenType.ELSE)
        self.assertEqual(tokens[3].type, TokenType.EOF)

    def test_unexpected_character(self):
        error_state["had_error"] = False  # Reset the flag before the test

        source = "@"
        scanner = Scanner(source)

        # Redirect stderr to capture the error message
        captured_output = StringIO()
        sys.stderr = captured_output

        scanner.scan_tokens()

        # Reset redirect.
        sys.stderr = sys.__stderr__

        self.assertTrue(error_state["had_error"])
        self.assertIn(
            "[line 1] Error: Unexpected character.", captured_output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
