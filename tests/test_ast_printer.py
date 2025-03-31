import unittest
from app.ast_printer import AstPrinter
from app.expr import Binary, Unary, Literal, Grouping


class TestAstPrinter(unittest.TestCase):
    def setUp(self):
        self.printer = AstPrinter()

    def test_literal(self):
        self.assertEqual(self.printer.print(Literal(123)), "123")
        self.assertEqual(self.printer.print(Literal(True)), "true")
        self.assertEqual(self.printer.print(Literal(False)), "false")
        self.assertEqual(self.printer.print(Literal(None)), "nil")

    def test_unary(self):
        expr = Unary("-", Literal(123))
        self.assertEqual(self.printer.print(expr), "(- 123)")

    def test_binary(self):
        expr = Binary(Literal(1), "+", Literal(2))
        self.assertEqual(self.printer.print(expr), "(+ 1 2)")

    def test_grouping(self):
        expr = Grouping(Literal(45.67))
        self.assertEqual(self.printer.print(expr), "(group 45.67)")

    def test_complex_expression(self):
        expr = Binary(Unary("-", Literal(123)), "*", Grouping(Literal(45.67)))
        self.assertEqual(self.printer.print(expr), "(* (- 123) (group 45.67))")


if __name__ == "__main__":
    unittest.main()
