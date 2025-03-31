import unittest
from app.parser import Parser
from app.ast_printer import AstPrinter
from app.token_type import TokenType
from app.token import Token


class TestParser(unittest.TestCase):
    def test_expression_to_string(self):
        tokens = [
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "123", 123, 1),
            Token(TokenType.STAR, "*", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.NUMBER, "45.67", 45.67, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "(* (- 123) (group 45.67))"
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
