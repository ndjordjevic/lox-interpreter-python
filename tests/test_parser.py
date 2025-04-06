import unittest
from app.parser import Parser
from app.ast_printer import AstPrinter
from app.token_type import TokenType
from app.token import Token


class TestParser(unittest.TestCase):
    def test_expression_to_string(self):
        # Define a list of tokens representing the expression: -123 * (45.67)
        tokens = [
            Token(TokenType.MINUS, "-", None, 1),  # Unary minus
            Token(TokenType.NUMBER, "123", 123, 1),  # Literal number 123
            Token(TokenType.STAR, "*", None, 1),  # Multiplication operator
            Token(TokenType.LEFT_PAREN, "(", None, 1),  # Left parenthesis
            Token(TokenType.NUMBER, "45.67", 45.67, 1),  # Literal number 45.67
            Token(TokenType.RIGHT_PAREN, ")", None, 1),  # Right parenthesis
            Token(TokenType.EOF, "", None, 1),  # End of file
        ]

        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "(* (- 123) (group 45.67))"
        self.assertEqual(result, expected)

    def test_unary_operators(self):
        # Test case: !false
        tokens = [
            Token(TokenType.BANG, "!", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "(! false)"
        self.assertEqual(result, expected)

        # Test case: !!true
        tokens = [
            Token(TokenType.BANG, "!", None, 1),
            Token(TokenType.BANG, "!", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "(! (! true))"
        self.assertEqual(result, expected)

    def test_parentheses(self):
        # Test case: ("foo")
        tokens = [
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.STRING, '"foo"', "foo", 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "(group foo)"
        self.assertEqual(result, expected)

        # Test case: ((true))
        tokens = [
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "(group (group true))"
        self.assertEqual(result, expected)

    def test_literals(self):
        # Test case: "quz hello"
        tokens = [
            Token(TokenType.STRING, '"quz hello"', "quz hello", 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "quz hello"
        self.assertEqual(result, expected)

        # Test case: 76
        tokens = [
            Token(TokenType.NUMBER, "76", 76.0, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "76.0"
        self.assertEqual(result, expected)

        # Test case: true
        tokens = [
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "true"
        self.assertEqual(result, expected)

        # Test case: nil
        tokens = [
            Token(TokenType.NIL, "nil", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "nil"
        self.assertEqual(result, expected)

    def test_unmatched_parenthesis(self):
        # Test case: (foo
        tokens = [
            Token(TokenType.LEFT_PAREN, "(", None, 1),  # Left parenthesis
            Token(TokenType.IDENTIFIER, "foo", "foo", 1),  # Identifier
            Token(TokenType.EOF, "", None, 1),  # End of file
        ]
        parser = Parser(tokens)

        with self.assertRaises(ParseError):  # Expect a ParseError
            parser.parse()


if __name__ == "__main__":
    unittest.main()
