import unittest
from unittest.mock import MagicMock
from app.lox_function import LoxFunction
from app.stmt import Function
from app.token import Token, TokenType
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

    def get(self, name):
        return self.last_environment.get(name)


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
        result = self.lox_function(interpreter, [123, 456])
        self.assertTrue(interpreter.executed_body)
        self.assertEqual(result, None)
        # Environment should have the parameters bound
        self.assertEqual(interpreter.last_environment.get(self.param_a), 123)
        self.assertEqual(interpreter.last_environment.get(self.param_b), 456)
        # The body passed to execute_block should be correct
        self.assertIs(interpreter.body, self.body)

    def test_initializer_returns_this(self):
        """Test that initializers return this instead of the return value"""
        # Create a dummy function declaration node for an initializer
        name_token = Token(TokenType.IDENTIFIER, "init", None, 1)
        body = [MagicMock()]
        declaration = Function(name_token, [], body)
        
        # Create an environment with a 'this' variable
        environment = Environment()
        instance = MagicMock()
        environment.define("this", instance)
        
        # Create the initializer function
        initializer = LoxFunction(declaration, environment, is_initializer=True)
        
        # Call the initializer
        interpreter = DummyInterpreter()
        result = initializer(interpreter, [])
        
        # Verify that it returns this instead of the return value
        self.assertIs(result, instance)
        self.assertTrue(interpreter.executed_body)


if __name__ == "__main__":
    unittest.main()
