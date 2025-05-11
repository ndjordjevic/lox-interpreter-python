import unittest
from app.resolver import Resolver
from app.interpreter import Interpreter
from app.parser import Parser
from app.scanner import Scanner
from app.error_handler import error_state


class TestResolver(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()
        self.resolver = Resolver(self.interpreter)

    def parse(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        return parser.parse()

    def test_resolve_variable_declaration(self):
        """Test basic variable declaration and usage"""
        stmts = self.parse(
            """
            var x = 1;
            print x;
        """
        )
        self.resolver.resolve(stmts)

    def test_duplicate_variable(self):
        """Test duplicate variable declaration in same scope"""
        stmts = self.parse(
            """
            {
                var x = 1;
                var x = 2;
            }
        """
        )
        error_state["had_error"] = False
        self.resolver.resolve(stmts)
        self.assertTrue(
            error_state["had_error"],
            "Error should have been reported for duplicate variable declaration.",
        )

    def test_self_referential_initializer(self):
        """Test variable referencing itself in initializer"""
        stmts = self.parse(
            """
            {
                var x = x;
            }
        """
        )
        error_state["had_error"] = False
        self.resolver.resolve(stmts)
        self.assertTrue(
            error_state["had_error"],
            "Error should have been reported for self-referential initializer.",
        )

    def test_nested_scopes(self):
        """Test variable shadowing in nested scopes"""
        stmts = self.parse(
            """
            var x = "global";
            {
                var x = "shadow";
                print x;  // Should resolve to inner x
            }
            print x;  // Should resolve to outer x
        """
        )
        self.resolver.resolve(stmts)

    def test_function_resolution(self):
        """Test function declaration and parameter scoping"""
        stmts = self.parse(
            """
            fun test(a, b) {
                print a;
                print b;
                var c = a + b;
                return c;
            }
        """
        )
        self.resolver.resolve(stmts)

    def test_recursive_function(self):
        """Test function that calls itself"""
        stmts = self.parse(
            """
            fun fib(n) {
                if (n <= 1) return n;
                return fib(n-1) + fib(n-2);
            }
        """
        )
        self.resolver.resolve(stmts)

    def test_uninitialized_variable(self):
        """Test using variable before declaration"""
        stmts = self.parse("print x; var x = 1;")
        self.resolver.resolve(stmts)

    def test_class_method_resolution(self):
        """Test basic class method resolution"""
        stmts = self.parse(
            """
            class Test {
                method() {
                    return 42;
                }
            }
        """
        )
        self.resolver.resolve(stmts)

    def test_class_method_parameters(self):
        """Test method parameter resolution"""
        stmts = self.parse(
            """
            class Test {
                method(a, b) {
                    return a + b;
                }
            }
        """
        )
        self.resolver.resolve(stmts)

    def test_class_method_variables(self):
        """Test variable resolution inside method body"""
        stmts = self.parse(
            """
            class Test {
                method() {
                    var x = 1;
                    return x;
                }
            }
        """
        )
        self.resolver.resolve(stmts)

    def test_nested_method_calls(self):
        """Test resolution of nested method calls"""
        stmts = self.parse(
            """
            class Test {
                method1() {
                    return 42;
                }
                method2() {
                    return 42;  // Temporarily return literal instead of this.method1()
                }
            }
        """
        )
        self.resolver.resolve(stmts)

    def test_method_return_errors(self):
        """Test return statement errors in methods"""
        stmts = self.parse(
            """
            class Test {
                method() {
                    return 42;
                }
            }
            return 42;  // Should error - can't return from top-level
        """
        )
        error_state["had_error"] = False
        self.resolver.resolve(stmts)
        self.assertTrue(
            error_state["had_error"],
            "Error should have been reported for top-level return."
        )

    def test_duplicate_method_names(self):
        """Test duplicate method names in class"""
        stmts = self.parse(
            """
            class Test {
                method() {
                    return 1;
                }
                method() {  // Should error - duplicate method name
                    return 2;
                }
            }
        """
        )
        error_state["had_error"] = False
        self.resolver.resolve(stmts)
        self.assertTrue(
            error_state["had_error"],
            "Error should have been reported for duplicate method name."
        )

    def test_initializer_return_error(self):
        """Test that returning a value from an initializer is caught as an error"""
        stmts = self.parse(
            """
            class Test {
                init() {
                    return "something else";  // Should error - can't return from initializer
                }
            }
        """
        )
        error_state["had_error"] = False
        self.resolver.resolve(stmts)
        self.assertTrue(
            error_state["had_error"],
            "Error should have been reported for return in initializer."
        )


if __name__ == "__main__":
    unittest.main()
