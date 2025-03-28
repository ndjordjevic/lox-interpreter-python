import sys
import unittest
from io import StringIO

from app import Scanner, TokenType, error_state


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
            "[line 1] Error: Unexpected character: @", captured_output.getvalue()
        )

    def test_parentheses(self):
        source = "(true)"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.LEFT_PAREN,
            TokenType.TRUE,
            TokenType.RIGHT_PAREN,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_nested_parentheses(self):
        source = "((nil))"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.LEFT_PAREN,
            TokenType.LEFT_PAREN,
            TokenType.NIL,
            TokenType.RIGHT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_string_literals(self):
        source = '"baz foo"'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "baz foo")
        self.assertEqual(tokens[1].type, TokenType.EOF)

    def test_number_literals(self):
        source = "77.50"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 77.5)
        self.assertEqual(tokens[1].type, TokenType.EOF)

    def test_booleans_and_nil(self):
        source = "true false nil"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NIL,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_reserved_words(self):
        source = "and or class if else"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.AND,
            TokenType.OR,
            TokenType.CLASS,
            TokenType.IF,
            TokenType.ELSE,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_unexpected_characters(self):
        source = "@#$"
        scanner = Scanner(source)

        # Redirect stderr to capture the error messages
        captured_output = StringIO()
        sys.stderr = captured_output

        scanner.scan_tokens()

        # Reset redirect
        sys.stderr = sys.__stderr__

        self.assertIn(
            "[line 1] Error: Unexpected character: @", captured_output.getvalue()
        )
        self.assertIn(
            "[line 1] Error: Unexpected character: #", captured_output.getvalue()
        )
        self.assertIn(
            "[line 1] Error: Unexpected character: $", captured_output.getvalue()
        )

    def test_empty_file(self):
        source = ""
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_whitespace(self):
        source = "   \t\n"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_single_line_comment(self):
        source = "// This is a comment"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_multiline_comment(self):
        source = "/* This is a\nmultiline comment */"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 1)  # Only EOF token should remain
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_unterminated_string(self):
        source = '"unterminated'
        scanner = Scanner(source)

        # Redirect stderr to capture the error message
        captured_output = StringIO()
        sys.stderr = captured_output

        scanner.scan_tokens()

        # Reset redirect
        sys.stderr = sys.__stderr__

        self.assertIn(
            "[line 1] Error: Unterminated string.", captured_output.getvalue()
        )

    def test_operators(self):
        source = "+-*/!=<>=="
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.BANG_EQUAL,
            TokenType.LESS,
            TokenType.GREATER_EQUAL,
            TokenType.EQUAL,  # This is correct for `==`
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_grouping_symbols(self):
        source = "(){}"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.RIGHT_BRACE,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_complex_expression(self):
        source = "var result = (a + b) > 7 or x >= 5"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.VAR,
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.LEFT_PAREN,
            TokenType.IDENTIFIER,
            TokenType.PLUS,
            TokenType.IDENTIFIER,
            TokenType.RIGHT_PAREN,
            TokenType.GREATER,
            TokenType.NUMBER,
            TokenType.OR,
            TokenType.IDENTIFIER,
            TokenType.GREATER_EQUAL,
            TokenType.NUMBER,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_reserved_words_and_identifiers(self):
        source = "and class else false for fun if nil or print return super this true var while"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.AND,
            TokenType.CLASS,
            TokenType.ELSE,
            TokenType.FALSE,
            TokenType.FOR,
            TokenType.FUN,
            TokenType.IF,
            TokenType.NIL,
            TokenType.OR,
            TokenType.PRINT,
            TokenType.RETURN,
            TokenType.SUPER,
            TokenType.THIS,
            TokenType.TRUE,
            TokenType.VAR,
            TokenType.WHILE,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_identifier_with_numbers(self):
        source = "foo123 _bar456"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.IDENTIFIER,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)

    def test_number_with_trailing_dot(self):
        source = "123."
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 123)
        self.assertEqual(tokens[1].type, TokenType.DOT)
        self.assertEqual(tokens[2].type, TokenType.EOF)

    def test_string_with_escape_characters(self):
        source = '"hello\\nworld"'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "hello\\nworld")
        self.assertEqual(tokens[1].type, TokenType.EOF)

    def test_multiline_string(self):
        source = '"hello\nworld"'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        # Verify the token type and literal value
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "hello\nworld")
        self.assertEqual(tokens[1].type, TokenType.EOF)

    def test_complex_nested_expression(self):
        source = "({()})"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.LEFT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.RIGHT_BRACE,
            TokenType.RIGHT_PAREN,
            TokenType.EOF,
        ]
        self.assertEqual(token_types, expected_types)


if __name__ == "__main__":
    unittest.main()
