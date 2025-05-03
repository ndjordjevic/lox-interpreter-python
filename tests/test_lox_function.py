import unittest
from unittest.mock import MagicMock
from app.lox_function import LoxFunction
from app.stmt import Function
from app.token import Token
from app.token_type import TokenType
from app.environment import Environment


class DummyInterpreter:
    def __init__(self):
        self.globals = Environment()
        self.executed_body = False
        self.last_environment = None

    def execute_block(self, body, environment):
        self.executed_body = True
        self.last_environment = environment
        self.body = body


class TestLoxFunction(unittest.TestCase):
    def setUp(self):
        # Create a dummy function declaration node
        self.name_token = Token(TokenType.IDENTIFIER, "foo", None, 1)
        self.param_a = Token(TokenType.IDENTIFIER, "a", None, 1)
        self.param_b = Token(TokenType.IDENTIFIER, "b", None, 1)
        self.body = [MagicMock()]
        self.declaration = Function(
            self.name_token, [self.param_a, self.param_b], self.body
        )
        self.lox_function = LoxFunction(self.declaration, Environment())

    def test_arity(self):
        self.assertEqual(self.lox_function.arity(), 2)

    def test_str(self):
        self.assertEqual(str(self.lox_function), "<fn foo>")

    def test_call_binds_parameters_and_executes_body(self):
        interpreter = DummyInterpreter()
        result = self.lox_function.call(interpreter, [123, 456])
        self.assertTrue(interpreter.executed_body)
        self.assertEqual(result, None)
        # Environment should have the parameters bound
        self.assertEqual(interpreter.last_environment.get(self.param_a), 123)
        self.assertEqual(interpreter.last_environment.get(self.param_b), 456)
        # The body passed to execute_block should be correct
        self.assertIs(interpreter.body, self.body)


if __name__ == "__main__":
    unittest.main()
