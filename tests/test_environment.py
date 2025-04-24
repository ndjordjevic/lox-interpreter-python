import unittest
from app.environment import Environment
from app.error_handler import RuntimeError


class MockToken:
    def __init__(self, lexeme):
        self.lexeme = lexeme


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_define_and_get(self):
        token = MockToken("x")
        self.env.define("x", 42)
        self.assertEqual(self.env.get(token), 42)

    def test_get_undefined_variable(self):
        token = MockToken("y")
        with self.assertRaises(RuntimeError) as context:
            self.env.get(token)
        self.assertEqual(str(context.exception), "Undefined variable 'y'.")

    def test_assign_existing_variable(self):
        token = MockToken("x")
        self.env.define("x", 42)
        self.env.assign(token, 100)
        self.assertEqual(self.env.get(token), 100)

    def test_assign_undefined_variable(self):
        token = MockToken("y")
        with self.assertRaises(RuntimeError) as context:
            self.env.assign(token, 100)
        self.assertEqual(str(context.exception), "Undefined variable 'y'.")

    def test_enclosing_environment(self):
        parent_env = Environment()
        child_env = Environment(enclosing=parent_env)
        parent_token = MockToken("a")
        child_token = MockToken("b")

        parent_env.define("a", 1)
        child_env.define("b", 2)

        self.assertEqual(child_env.get(parent_token), 1)
        self.assertEqual(child_env.get(child_token), 2)

        child_env.assign(parent_token, 42)
        self.assertEqual(parent_env.get(parent_token), 42)


if __name__ == "__main__":
    unittest.main()
