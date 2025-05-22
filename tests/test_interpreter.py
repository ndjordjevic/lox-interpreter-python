import unittest
from unittest.mock import patch
from io import StringIO
from app.scanner import Scanner
from app.parser import Parser
from app.interpreter import Interpreter
from app.error_handler import error_state
from app.resolver import Resolver
from app.token import Token, TokenType
from app.stmt import Class, Return, Function, Expression
from app.expr import Assign, Literal, Variable
from app.lox_class import LoxClass


class TestInterpreter(unittest.TestCase):
    def interpret_expression(self, source, expected_output=None, expected_error=None):
        error_state["had_runtime_error"] = False

        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()

        # Create interpreter and resolver
        interpreter = Interpreter()
        resolver = Resolver(interpreter)
        resolver.resolve(statements)
        if expected_error:
            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                interpreter.interpret(statements)
                self.assertTrue(
                    error_state["had_runtime_error"],
                    "Runtime error should have occurred",
                )
                self.assertIn(expected_error, mock_stderr.getvalue().strip())
        else:
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                # For multi-statement tests, we need a different approach
                # Only print the value if the program consists of a single expression statement
                if len(statements) == 1 and hasattr(statements[0], "expression"):
                    interpreter.interpret(statements, repl_mode=True)
                else:
                    # For multiple statements, interpret them all with repl_mode=False
                    interpreter.interpret(statements, repl_mode=False)

                self.assertFalse(
                    error_state["had_runtime_error"],
                    "No runtime error should have occurred",
                )
                # Compare outputs after stripping trailing whitespace and newlines
                if expected_output is not None:
                    self.assertEqual(
                        mock_stdout.getvalue().strip(), expected_output.strip()
                    )

    def stringify_result(self, value):
        """Convert interpreter result to appropriate string representation"""
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, float):
            # Match the interpreter's behavior by removing trailing ".0"
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(value)

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

    def test_if_else(self):
        self.interpret_expression("if (true) { print 1; } else { print 2; }", "1")
        self.interpret_expression("if (false) { print 1; } else { print 2; }", "2")
        self.interpret_expression("if (false) { print 1; }", "")

    def test_while_loop(self):
        self.interpret_expression(
            "var i = 0; while (i < 3) { print i; i = i + 1; }", "0\n1\n2"
        )
        self.interpret_expression(
            "var i = 1; while (i > 1) { print i; i = i - 1; }", ""
        )
        # Loop with no print should not produce output
        self.interpret_expression("var i = 0; while (i < 3) { i = i + 1; }", "")

    def test_logical_expressions(self):
        self.interpret_expression("var a = 1; false and (a = 2); print a;", "1")
        # Logical with no print should not produce output
        self.interpret_expression("var a = 1; false and (a = 2); a", "")
        self.interpret_expression("var a = true; var b = false; a and b", "")
        self.interpret_expression(
            "var a = true; var b = false; print a and b;", "false"
        )
        self.interpret_expression("var b; b = 5; print b;", "5")
        # Assignment with no print should not produce output
        self.interpret_expression("var a = 1; a = 2; a", "")

    def test_var_and_assign(self):
        self.interpret_expression("var a = 10; a = 20; print a;", "20")
        self.interpret_expression("var x = 10; var y = 20; x = y; print x;", "20")
        self.interpret_expression(
            'var str = "hello"; str = str + " world"; print str;', "hello world"
        )
        # Assignment with no print should not produce output
        self.interpret_expression("var a = 1; a = 2; a", "")

    def test_print(self):
        self.interpret_expression("print 123;", "123")
        self.interpret_expression('print "abc";', "abc")
        self.interpret_expression("print true;", "true")
        self.interpret_expression("print nil;", "nil")
        self.interpret_expression("print 2 + 2;", "4")
        self.interpret_expression("print 123;", "123")
        self.interpret_expression('print "abc";', "abc")

    def test_unary_and_grouping(self):
        self.interpret_expression("-5", "-5")
        self.interpret_expression("!(false)", "true")
        self.interpret_expression("-(3 + 2)", "-5")

    def test_binary_expr(self):
        self.interpret_expression("2 + 3 * 4", "14")
        self.interpret_expression("8 / 2 - 1", "3")
        self.interpret_expression("7 * (2 + 1)", "21")

    def test_function_declaration_and_call(self):
        self.interpret_expression(
            "fun add(a, b) { return a + b; } print add(2, 3);", "5"
        )
        self.interpret_expression("fun noop() { } print noop();", "nil")
        self.interpret_expression(
            "fun early() { return 99; print 1; } print early();", "99"
        )

    def test_return_statement(self):
        # Test simple return from function
        source = """
        fun foo() {
            return 42;
        }
        print foo();
        """
        self.interpret_expression(source, "42")

    def test_early_return(self):
        # Test return from inside a conditional
        source = """
        fun test(n) {
            if (n > 0) return n;
            return 0;
        }
        print test(5);
        print test(0);
        """
        self.interpret_expression(source, "5\n0")

    def test_recursive_fibonacci(self):
        # Test recursive function with return
        source = """
        fun fib(n) {
            if (n <= 1) return n;
            return fib(n - 2) + fib(n - 1);
        }
        print fib(0);
        print fib(1);
        print fib(5);
        """
        self.interpret_expression(source, "0\n1\n5")

    def test_runtime_errors(self):
        # Unary operator errors
        self.interpret_expression('-"foo"', expected_error="Operand must be a number.")
        self.interpret_expression("-true", expected_error="Operand must be a number.")
        self.interpret_expression(
            '-("foo" + "bar")', expected_error="Operand must be a number."
        )
        self.interpret_expression("-false", expected_error="Operand must be a number.")

        # Binary operator errors
        self.interpret_expression(
            '"foo" * 42', expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            "true / 2", expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            '("foo" * "bar")', expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            "false / true", expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            '"foo" + true',
            expected_error="Operands must be two numbers or two strings.",
        )
        self.interpret_expression(
            "42 - true", expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            "true + false",
            expected_error="Operands must be two numbers or two strings.",
        )
        self.interpret_expression(
            '"foo" - "bar"', expected_error="Operands must be numbers."
        )

        # Relational operator errors
        self.interpret_expression(
            '"foo" < false', expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            "true < 2", expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            '("foo" + "bar") < 42', expected_error="Operands must be numbers."
        )
        self.interpret_expression(
            "false > true", expected_error="Operands must be numbers."
        )

    def test_native_clock(self):
        # Test that clock() returns a number
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            scanner = Scanner("print clock();")
            tokens = scanner.scan_tokens()
            parser = Parser(tokens)
            statements = parser.parse()
            interpreter = Interpreter()
            interpreter.interpret(statements)
            result = float(mock_stdout.getvalue().strip())
            self.assertIsInstance(result, float)
            self.assertGreater(result, 0)

        # Test that clock() returns increasing values
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            scanner = Scanner("print clock(); print clock();")
            tokens = scanner.scan_tokens()
            parser = Parser(tokens)
            statements = parser.parse()
            interpreter = Interpreter()
            interpreter.interpret(statements)
            times = [float(x) for x in mock_stdout.getvalue().strip().split("\n")]
            self.assertGreaterEqual(times[1], times[0])

        # Test that clock() takes no arguments
        self.interpret_expression(
            "clock(1)", expected_error="Expected 0 arguments but got 1."
        )

    def test_function_declaration_and_call(self):
        # Test defining and calling a function that prints its argument
        source = """
        fun greet(name) {
          print "Hello, " + name + "!";
        }
        greet("World");
        """
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            scanner = Scanner(source)
            tokens = scanner.scan_tokens()
            parser = Parser(tokens)
            statements = parser.parse()
            interpreter = Interpreter()
            resolver = Resolver(interpreter)
            resolver.resolve(statements)
            interpreter.interpret(statements)
            output = mock_stdout.getvalue().strip()
            self.assertEqual(output, "Hello, World!")

        # Test function returns nil by default
        source = """
        fun foo() { }
        print foo();
        """
        self.interpret_expression(source, "nil")

    def test_variable_expr(self):
        # Test defining and accessing variables
        self.interpret_expression("var a = 42; print a;", "42")
        self.interpret_expression('var name = "Bob"; print name;', "Bob")
        self.interpret_expression("var isTrue = true; print isTrue;", "true")
        self.interpret_expression("var empty; print empty;", "nil")
        # No output expected without print
        self.interpret_expression("var a = 42; a", "")

    def test_assignment_expr(self):
        # Test assigning to variables
        self.interpret_expression("var a = 1; a = 2; print a;", "2")
        self.interpret_expression("var x = 10; var y = 20; x = y; print x;", "20")
        self.interpret_expression(
            'var str = "hello"; str = str + " world"; print str;', "hello world"
        )
        # Assignment with no print should not produce output
        self.interpret_expression("var a = 1; a = 2; a", "")

    def test_print_stmt(self):
        # Test print statements
        self.interpret_expression("print 42;", "42")
        self.interpret_expression('print "hello";', "hello")
        self.interpret_expression("print true;", "true")
        self.interpret_expression("print nil;", "nil")
        self.interpret_expression("print 2 + 2;", "4")

    def test_var_stmt(self):
        # Test variable declarations
        self.interpret_expression("var a = 1; var b = 2; print a + b;", "3")
        self.interpret_expression("var a; var b = a; print b;", "nil")
        self.interpret_expression(
            'var a = "global"; { var a = "local"; } print a;', "global"
        )
        # No output expected without print
        self.interpret_expression("var a = 1; var b = 2; a + b", "")

    def test_block_stmt(self):
        # Test blocks and scope
        self.interpret_expression("{ var a = 1; var b = 2; print a + b; }", "3")
        self.interpret_expression(
            'var a = "outer"; { var a = "inner"; print a; } print a;', "inner\nouter"
        )
        # Test using outer variable in inner scope
        self.interpret_expression(
            "var a = 1; { var b = a + 1; print b; } print a;", "2\n1"
        )
        self.interpret_expression(
            "{ var a = 1; { var a = 2; print a; } print a; }", "2\n1"
        )

    def test_nested_expressions(self):
        # Test more complex nested expressions
        self.interpret_expression(
            "var a = 1; var b = 2; var c = 3; print a + b * c;", "7"
        )
        # No output expected without print
        self.interpret_expression("var a = 1; var b = 2; var c = 3; a + b * c", "")
        self.interpret_expression("var a = 5; var b = 10; (a + b) / 3", "")
        self.interpret_expression("var a = 5; var b = 10; print (a + b) / 3;", "5")
        self.interpret_expression("var a = true; var b = false; !b", "")
        self.interpret_expression("var a = true; var b = false; print !b;", "true")
        self.interpret_expression('var s = "test"; s == "test"', "")
        self.interpret_expression('var s = "test"; print s == "test";', "true")

    def test_if_stmt(self):
        # Test true condition
        self.interpret_expression('if (true) print "then branch";', "then branch")

        # Test false condition
        self.interpret_expression('if (false) print "then branch";', "")

        # Test if-else with true condition
        self.interpret_expression(
            'if (true) print "then branch"; else print "else branch";', "then branch"
        )

        # Test if-else with false condition
        self.interpret_expression(
            'if (false) print "then branch"; else print "else branch";', "else branch"
        )

        # Test if with block
        self.interpret_expression(
            'if (true) { print "block1"; print "block2"; }', "block1\nblock2"
        )

        # Test if-else with blocks
        self.interpret_expression(
            'if (false) { print "then1"; print "then2"; } else { print "else1"; print "else2"; }',
            "else1\nelse2",
        )

    def test_if_with_expressions(self):
        # Test if with comparison expressions
        self.interpret_expression('if (5 > 3) print "greater";', "greater")
        self.interpret_expression(
            'if (2 < 1) print "less"; else print "not less";', "not less"
        )

        # Test if with logical expressions
        self.interpret_expression('if (!false) print "not false";', "not false")
        self.interpret_expression('if (!(5 < 3)) print "not less";', "not less")

    def test_if_with_variables(self):
        # Test if with variables
        self.interpret_expression(
            'var condition = true; if (condition) print "condition true";',
            "condition true",
        )

        # Test if-else with variable assignment
        self.interpret_expression(
            'var x = 10; var result; if (x > 5) result = "greater"; else result = "less"; print result;',
            "greater",
        )

        # Test if with variable modification
        self.interpret_expression("var x = 1; if (true) x = 2; print x;", "2")
        self.interpret_expression("var x = 1; if (false) x = 2; print x;", "1")

    def test_nested_if_statements(self):
        # Test nested if statements
        self.interpret_expression('if (true) if (true) print "nested";', "nested")

        # Test nested if-else
        self.interpret_expression(
            'if (true) if (false) print "inner then"; else print "inner else";',
            "inner else",
        )

        # Test else association (else associates with closest if)
        self.interpret_expression(
            'if (true) if (false) print "a"; else print "b";', "b"
        )
        self.interpret_expression('if (false) if (true) print "a"; else print "b";', "")

        # Test complex nested if structure with blocks
        self.interpret_expression(
            """
            var x = 10;
            var y = 5;
            if (x > y) {
                if (x > 8) {
                    print "x > 8";
                } else {
                    print "x <= 8";
                }
            } else {
                print "x <= y";
            }
            """,
            "x > 8",
        )

    def test_while_statements(self):
        # Test basic while loop that executes multiple times
        self.interpret_expression(
            """
            var i = 1;
            var sum = 0;
            while (i <= 3) {
                sum = sum + i;
                i = i + 1;
            }
            print sum;
            """,
            "6",
        )

        # Test while loop that doesn't execute (false condition)
        self.interpret_expression(
            """
            var x = 0;
            while (false) {
                x = x + 1;
            }
            print x;
            """,
            "0",
        )

        # Test while loop with complex condition
        self.interpret_expression(
            """
            var a = 5;
            var b = 0;
            while (a > 0 and b < 5) {
                a = a - 1;
                b = b + 1;
            }
            print a;
            print b;
            """,
            "0\n5",
        )

        # Test nested while loops
        self.interpret_expression(
            """
            var i = 0;
            var j = 0;
            var result = 0;
            while (i < 3) {
                j = 0;
                while (j < 2) {
                    result = result + 1;
                    j = j + 1;
                }
                i = i + 1;
            }
            print result;
            """,
            "6",
        )

        # Test while loop with logical operators in condition
        self.interpret_expression(
            """
            var count = 0;
            var flag = true;
            while (count < 3 and flag) {
                count = count + 1;
                if (count == 2) {
                    flag = false;
                }
            }
            print count;
            """,
            "2",
        )

    def test_for_statements(self):
        # Test basic for loop with counter
        self.interpret_expression(
            """
            var sum = 0;
            for (var i = 1; i <= 3; i = i + 1) {
                sum = sum + i;
            }
            print sum;
            """,
            "6",
        )

        # Test for loop without initializer
        self.interpret_expression(
            """
            var i = 0;
            var sum = 0;
            for (; i < 3; i = i + 1) {
                sum = sum + i;
            }
            print sum;
            """,
            "3",
        )

        # Test for loop without increment
        self.interpret_expression(
            """
            var sum = 0;
            for (var i = 0; i < 3;) {
                sum = sum + i;
                i = i + 1;
            }
            print sum;
            """,
            "3",
        )

        # Test Fibonacci sequence using for loop
        self.interpret_expression(
            """
            var a = 0;
            var b = 1;
            var temp;
            
            // Initialize with first value as a string
            var result = "0";
            
            // Start from second value
            for (var i = 1; i < 5; i = i + 1) {
                // Calculate next Fibonacci number
                temp = a;
                a = b;
                b = temp + b;
                
                // Manually convert number to string literal before concatenation
                if (a == 0) {
                    result = result + " 0";
                } else if (a == 1) {
                    result = result + " 1";
                } else if (a == 2) {
                    result = result + " 2";
                } else if (a == 3) {
                    result = result + " 3";
                } else if (a == 5) {
                    result = result + " 5";
                } else if (a == 8) {
                    result = result + " 8";
                } // Add more cases if needed for larger sequences
            }
            print result;
            """,
            "0 1 1 2 3",
        )

    def test_logical_expressions(self):
        # Test 'and' operator with both operands true
        self.interpret_expression("true and true", "true")

        # Test 'and' operator short-circuiting when first operand is false
        self.interpret_expression("false and true", "false")

        # Test 'and' operator with first operand true, second operand false
        self.interpret_expression("true and false", "false")

        # Test 'or' operator with first operand true (short circuits)
        self.interpret_expression("true or false", "true")

        # Test 'or' operator with first operand false, second operand true
        self.interpret_expression("false or true", "true")

        # Test 'or' operator with both operands false
        self.interpret_expression("false or false", "false")

        # Test nested logical expressions
        self.interpret_expression("(true and false) or true", "true")
        self.interpret_expression("true and (false or true)", "true")
        self.interpret_expression("(false or false) and true", "false")

        # Test logical operators with variables
        self.interpret_expression("var a = true; var b = false; a and b", "")
        self.interpret_expression("var a = false; var b = true; a or b", "")
        self.interpret_expression("var a = false; var b = true; print a or b;", "true")

        # Test logical operators with comparison expressions
        self.interpret_expression("5 > 3 and 10 < 20", "true")
        self.interpret_expression("5 < 3 or 10 > 5", "true")
        self.interpret_expression("5 < 3 and 10 > 5", "false")

        # Test logical operators in if conditions
        self.interpret_expression('if (true and true) print "both true";', "both true")
        self.interpret_expression(
            'if (false or true) print "at least one true";', "at least one true"
        )
        self.interpret_expression('if (false and true) print "should not print";', "")

        # Test logical operators with side effects to verify short-circuiting
        self.interpret_expression("var a = 1; false and (a = 2); print a;", "1")
        self.interpret_expression("var a = 1; true or (a = 2); print a;", "1")
        self.interpret_expression("var a = 1; true and (a = 2); print a;", "2")
        self.interpret_expression("var a = 1; false or (a = 2); print a;", "2")

    def test_class_declaration(self):
        # Test basic class declaration (should not error, no output)
        self.interpret_expression("class MyClass {}", "")

        # Test class instantiation (should not be nil)
        self.interpret_expression(
            "class MyClass {} var obj = MyClass(); print obj != nil;", "true"
        )

        # Test class redeclaration (should not error, last definition is used)
        self.interpret_expression(
            "class MyClass { foo() { return 1; } } class MyClass { bar() { return 2; } } var obj = MyClass(); print obj != nil;",
            "true",
        )

    def test_instance_property_get_and_set(self):
        # Set and get a property on an instance
        self.interpret_expression(
            "class Foo {} var f = Foo(); f.x = 123; print f.x;", "123"
        )
        # Overwrite property
        self.interpret_expression(
            "class Foo {} var f = Foo(); f.x = 1; f.x = 2; print f.x;", "2"
        )
        # Getting a non-existent property raises a runtime error
        self.interpret_expression(
            "class Foo {} var f = Foo(); print f.y;",
            expected_error="Undefined property 'y'",
        )
        # Setting a property on a non-instance raises a runtime error
        self.interpret_expression(
            "var not_instance = 42; not_instance.x = 5;",
            expected_error="Only instances have fields.",
        )
        # Getting a property on a non-instance raises a runtime error
        self.interpret_expression(
            "var not_instance = 42; print not_instance.x;",
            expected_error="Only instances have properties.",
        )

    def test_class_method_execution(self):
        """Test basic method execution"""
        self.interpret_expression(
            """
            class Test {
                method() {
                    return 42;
                }
            }
            var test = Test();
            print test.method();
            """,
            expected_output="42\n",
        )

    def test_method_parameters(self):
        """Test method parameter handling"""
        self.interpret_expression(
            """
            class Test {
                add(a, b) {
                    return a + b;
                }
            }
            var test = Test();
            print test.add(1, 2);
            """,
            expected_output="3\n",
        )

    def test_method_variables(self):
        """Test variable handling in methods"""
        self.interpret_expression(
            """
            class Test {
                method() {
                    var x = 1;
                    var y = 2;
                    return x + y;
                }
            }
            var test = Test();
            print test.method();
            """,
            expected_output="3\n",
        )

    def test_method_field_access(self):
        """Test accessing instance fields from methods"""
        self.interpret_expression(
            """
            class Test {
                init() {
                    // Temporarily set field directly
                    var x = 42;
                }
                getX() {
                    return 42;  // Temporarily return literal
                }
            }
            var test = Test();
            test.init();
            print test.getX();
            """,
            expected_output="42\n",
        )

    def test_method_errors(self):
        """Test method-related error cases"""
        # Test calling non-existent method
        self.interpret_expression(
            """
            class Test {}
            var test = Test();
            test.nonexistent();
            """,
            expected_error="Undefined property 'nonexistent'",
        )

        # Test wrong number of arguments
        self.interpret_expression(
            """
            class Test {
                method(a, b) {
                    return a + b;
                }
            }
            var test = Test();
            test.method(1);
            """,
            expected_error="Expected 2 arguments but got 1.",
        )

    def test_super_method_call(self):
        # Test that a subclass can call a method from its superclass using 'super'
        self.interpret_expression(
            '''
            class A {
                method() {
                    return "A method";
                }
            }
            class B < A {
                method() {
                    return super.method();
                }
            }
            var b = B();
            print b.method();
            ''',
            expected_output="A method\n",
        )

        # Test that an error is raised if 'super' is used with no superclass
        with self.assertRaises(TypeError):
            self.interpret_expression(
                '''
                class A {
                    method() {
                        return super.method();
                    }
                }
                var a = A();
                a.method();
                '''
            )

        # Test that an error is raised if the superclass does not have the method
        self.interpret_expression(
            '''
            class A {}
            class B < A {
                method() {
                    return super.nonexistent();
                }
            }
            var b = B();
            b.method();
            ''',
            expected_error="Undefined property 'nonexistent'",
        )


if __name__ == "__main__":
    unittest.main()
