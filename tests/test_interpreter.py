import unittest
from unittest.mock import patch
from io import StringIO
from app.scanner import Scanner
from app.parser import Parser
from app.interpreter import Interpreter
from app.error_handler import runtime_error, error_state

class TestInterpreter(unittest.TestCase):
    def interpret_expression(self, source, expected_output=None, expected_error=None):
        # Reset error state before test
        error_state["had_runtime_error"] = False

        # Scan the source code
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        # Parse the tokens into an AST
        parser = Parser(tokens)
        expression = parser.parse()

        # Interpret the AST and capture the output or error
        interpreter = Interpreter()
        if expected_error:
            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                interpreter.interpret(expression)
                self.assertTrue(
                    error_state["had_runtime_error"],
                    "Runtime error should have occurred",
                )
                self.assertIn(expected_error, mock_stderr.getvalue().strip())
        else:
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                interpreter.interpret(expression)
                self.assertFalse(
                    error_state["had_runtime_error"],
                    "No runtime error should have occurred",
                )
                self.assertEqual(mock_stdout.getvalue().strip(), expected_output)

    def test_literal_expression(self):
        # Test interpreting a literal number
        self.interpret_expression("42", "42")
        self.interpret_expression("true", "true")
        self.interpret_expression("false", "false")
        self.interpret_expression("nil", "nil")

    def test_unary_expression(self):
        # Test interpreting a unary minus
        self.interpret_expression("-42", "-42")
        self.interpret_expression("!true", "false")
        self.interpret_expression("!false", "true")

    def test_binary_expression(self):
        # Test interpreting a binary addition
        self.interpret_expression("5 + 3", "8")
        self.interpret_expression("10 - 4", "6")
        self.interpret_expression("8 / 2", "4")
        self.interpret_expression("7 * 3", "21")

    def test_grouping_expression(self):
        # Test interpreting a grouped expression
        self.interpret_expression("(1 + 2) * 3", "9")

    def test_comparison_expression(self):
        # Test interpreting a comparison
        self.interpret_expression("5 > 3", "true")
        self.interpret_expression("3 < 5", "true")
        self.interpret_expression("3 <= 3", "true")
        self.interpret_expression("5 >= 3", "true")
        self.interpret_expression("5 > 7", "false")

    def test_equality_expression(self):
        # Test interpreting an equality
        self.interpret_expression("5 == 5", "true")
        self.interpret_expression("5 != 3", "true")

    def test_string_concatenation(self):
        # Test interpreting string concatenation
        self.interpret_expression('"Hello, " + "world!"', "Hello, world!")

    def test_runtime_errors(self):
        # Unary operator errors
        self.interpret_expression('-"foo"', expected_error="Operand must be a number.")
        self.interpret_expression("-true", expected_error="Operand must be a number.")
        self.interpret_expression(
            '-("foo" + "bar")', expected_error="Operand must be a number."
        )
        self.interpret_expression("-false", expected_error="Operand must be a number.")

        # Binary operator errors
        self.interpret_expression('"foo" * 42', expected_error="Operands must be numbers.")
        self.interpret_expression("true / 2", expected_error="Operands must be numbers.")
        self.interpret_expression(
            '("foo" * "bar")', expected_error="Operands must be numbers."
        )
        self.interpret_expression("false / true", expected_error="Operands must be numbers.")
        self.interpret_expression(
            '"foo" + true', expected_error="Operands must be two numbers or two strings."
        )
        self.interpret_expression("42 - true", expected_error="Operands must be numbers.")
        self.interpret_expression(
            "true + false", expected_error="Operands must be two numbers or two strings."
        )
        self.interpret_expression('"foo" - "bar"', expected_error="Operands must be numbers.")

        # Relational operator errors
        self.interpret_expression('"foo" < false', expected_error="Operands must be numbers.")
        self.interpret_expression("true < 2", expected_error="Operands must be numbers.")
        self.interpret_expression(
            '("foo" + "bar") < 42', expected_error="Operands must be numbers."
        )
        self.interpret_expression("false > true", expected_error="Operands must be numbers.")

if __name__ == "__main__":
    unittest.main()
