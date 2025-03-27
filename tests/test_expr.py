import unittest
import sys
import os

# Add the parent directory of 'tests' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.expr import Binary, Grouping, Literal, Unary, Evaluator


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def test_literal(self):
        expression = Literal(42)
        result = expression.accept(self.evaluator)
        self.assertEqual(result, 42)

    def test_unary(self):
        expression = Unary("-", Literal(42))
        result = expression.accept(self.evaluator)
        self.assertEqual(result, -42)

    def test_binary_addition(self):
        expression = Binary(Literal(1), "+", Literal(2))
        result = expression.accept(self.evaluator)
        self.assertEqual(result, 3)

    def test_binary_subtraction(self):
        expression = Binary(Literal(5), "-", Literal(3))
        result = expression.accept(self.evaluator)
        self.assertEqual(result, 2)

    def test_binary_multiplication(self):
        expression = Binary(Literal(2), "*", Literal(3))
        result = expression.accept(self.evaluator)
        self.assertEqual(result, 6)

    def test_binary_division(self):
        expression = Binary(Literal(8), "/", Literal(2))
        result = expression.accept(self.evaluator)
        self.assertEqual(result, 4)

    def test_grouping(self):
        expression = Grouping(Literal(42))
        result = expression.accept(self.evaluator)
        self.assertEqual(result, 42)

    def test_complex_expression(self):
        expression = Binary(Unary("-", Literal(123)), "*", Grouping(Literal(45.67)))
        result = expression.accept(self.evaluator)
        self.assertEqual(result, -123 * 45.67)


if __name__ == "__main__":
    unittest.main()
