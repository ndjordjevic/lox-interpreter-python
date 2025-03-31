import unittest
from app.rpn_printer import RpnPrinter
from app.expr import Binary, Grouping, Literal, Unary


class TestRpnPrinter(unittest.TestCase):
    def setUp(self):
        self.printer = RpnPrinter()

    def test_literal(self):
        expr = Literal(42)
        self.assertEqual(self.printer.print(expr), "42")

    def test_binary(self):
        expr = Binary(Literal(1), "+", Literal(2))
        self.assertEqual(self.printer.print(expr), "1 2 +")

    def test_grouping(self):
        expr = Grouping(Literal(3))
        self.assertEqual(self.printer.print(expr), "3")

    def test_unary(self):
        expr = Unary("-", Literal(5))
        self.assertEqual(self.printer.print(expr), "5 -")

    def test_complex_expression(self):
        expr = Binary(
            Binary(Literal(1), "+", Literal(2)),
            "*",
            Binary(Literal(4), "-", Literal(3)),
        )
        self.assertEqual(self.printer.print(expr), "1 2 + 4 3 - *")


if __name__ == "__main__":
    unittest.main()
