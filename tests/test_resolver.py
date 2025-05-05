import unittest
from app.resolver import Resolver
from app.interpreter import Interpreter
from app.parser import Parser
from app.scanner import Scanner

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
        stmts = self.parse("""
            var x = 1;
            print x;
        """)
        self.resolver.resolve(stmts)
    
    def test_duplicate_variable(self):
        """Test duplicate variable declaration in same scope"""
        stmts = self.parse("""
            {
                var x = 1;
                var x = 2;
            }
        """)
        with self.assertRaises(Exception) as context:
            self.resolver.resolve(stmts)
        self.assertIn("Variable x already declared", str(context.exception))
    
    def test_self_referential_initializer(self):
        """Test variable referencing itself in initializer"""
        stmts = self.parse("""
            {
                var x = x;
            }
        """)
        with self.assertRaises(Exception) as context:
            self.resolver.resolve(stmts)
        self.assertIn("Can't read local variable x in its own initializer", 
                     str(context.exception))
    
    def test_nested_scopes(self):
        """Test variable shadowing in nested scopes"""
        stmts = self.parse("""
            var x = "global";
            {
                var x = "shadow";
                print x;  // Should resolve to inner x
            }
            print x;  // Should resolve to outer x
        """)
        self.resolver.resolve(stmts)
    
    def test_function_resolution(self):
        """Test function declaration and parameter scoping"""
        stmts = self.parse("""
            fun test(a, b) {
                print a;
                print b;
                var c = a + b;
                return c;
            }
        """)
        self.resolver.resolve(stmts)
    
    def test_recursive_function(self):
        """Test function that calls itself"""
        stmts = self.parse("""
            fun fib(n) {
                if (n <= 1) return n;
                return fib(n-1) + fib(n-2);
            }
        """)
        self.resolver.resolve(stmts)
    
    def test_uninitialized_variable(self):
        """Test using variable before declaration"""
        stmts = self.parse("print x; var x = 1;")
        self.resolver.resolve(stmts)

if __name__ == "__main__":
    unittest.main()
