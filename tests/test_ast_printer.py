import unittest
from app.ast_printer import AstPrinter
from app.expr import Binary, Unary, Literal, Grouping
from app.token import Token
from app.token_type import TokenType


class TestAstPrinter(unittest.TestCase):
    def setUp(self):
        self.printer = AstPrinter()

    def test_literal(self):
        self.assertEqual(self.printer.print(Literal(123)), "123")
        self.assertEqual(self.printer.print(Literal(True)), "true")
        self.assertEqual(self.printer.print(Literal(False)), "false")
        self.assertEqual(self.printer.print(Literal(None)), "nil")

    def test_unary(self):
        # Use a Token object for the operator
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        expr = Unary(minus_token, Literal(123))
        self.assertEqual(self.printer.print(expr), "(- 123)")

    def test_binary(self):
        # Use a Token object for the operator
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        expr = Binary(Literal(1), plus_token, Literal(2))
        self.assertEqual(self.printer.print(expr), "(+ 1 2)")

    def test_grouping(self):
        expr = Grouping(Literal(45.67))
        self.assertEqual(self.printer.print(expr), "(group 45.67)")

    def test_complex_expression(self):
        # Use Token objects for the operators
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        star_token = Token(TokenType.STAR, "*", None, 1)
        expr = Binary(Unary(minus_token, Literal(123)), star_token, Grouping(Literal(45.67)))
        self.assertEqual(self.printer.print(expr), "(* (- 123) (group 45.67))")


if __name__ == "__main__":
    unittest.main()
