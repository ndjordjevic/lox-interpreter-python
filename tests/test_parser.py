import unittest
from app.parser import Parser
from app.ast_printer import AstPrinter
from app.token_type import TokenType
from app.token import Token
from app.error_handler import error_state
from app.expr import Literal, Call, Variable

class TestParser(unittest.TestCase):
    def test_expression_to_string(self):
        # Define a list of tokens representing the expression: -123 * (45.67)
        tokens = [
            Token(TokenType.MINUS, "-", None, 1),  # Unary minus
            Token(TokenType.NUMBER, "123", 123, 1),  # Literal number 123
            Token(TokenType.STAR, "*", None, 1),  # Multiplication operator
            Token(TokenType.LEFT_PAREN, "(", None, 1),  # Left parenthesis
            Token(TokenType.NUMBER, "45.67", 45.67, 1),  # Literal number 45.67
            Token(TokenType.RIGHT_PAREN, ")", None, 1),  # Right parenthesis
            Token(TokenType.EOF, "", None, 1),  # End of file
        ]

        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "(* (- 123) (group 45.67))"
        self.assertEqual(result, expected)

    def test_unary_operators(self):
        # Test case: !false
        tokens = [
            Token(TokenType.BANG, "!", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "(! false)"
        self.assertEqual(result, expected)

        # Test case: !!true
        tokens = [
            Token(TokenType.BANG, "!", None, 1),
            Token(TokenType.BANG, "!", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "(! (! true))"
        self.assertEqual(result, expected)

    def test_parentheses(self):
        # Test case: ("foo")
        tokens = [
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.STRING, '"foo"', "foo", 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "(group foo)"
        self.assertEqual(result, expected)

        # Test case: ((true))
        tokens = [
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "(group (group true))"
        self.assertEqual(expected, result)

    def test_literals(self):
        # Test case: "quz hello"
        tokens = [
            Token(TokenType.STRING, '"quz hello"', "quz hello", 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(expression)

        expected = "quz hello"
        self.assertEqual(result, expected)

        # Test case: 76
        tokens = [
            Token(TokenType.NUMBER, "76", 76.0, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "76.0"
        self.assertEqual(result, expected)

        # Test case: true
        tokens = [
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "true"
        self.assertEqual(result, expected)

        # Test case: nil
        tokens = [
            Token(TokenType.NIL, "nil", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        expression = parser.parse()

        result = ast_printer.print(expression)
        expected = "nil"
        self.assertEqual(result, expected)

    def test_unmatched_parenthesis(self):
        # Test case: (foo
        tokens = [
            Token(TokenType.LEFT_PAREN, "(", None, 1),  # Left parenthesis
            Token(TokenType.IDENTIFIER, "foo", "foo", 1),  # Identifier
            Token(TokenType.EOF, "", None, 1),  # End of file
        ]
        parser = Parser(tokens)

        # Reset error state before test
        error_state["had_error"] = False

        result = parser.parse()
        # The parser returns [None] when there's an error (not None)
        self.assertEqual([None], result, "Parser should return [None] on error")
        self.assertTrue(error_state["had_error"], "Error state should be set")

    def test_equality_expressions(self):
        # Test equality (==) expression
        tokens = [
            Token(TokenType.NUMBER, "5", 5.0, 1),
            Token(TokenType.EQUAL_EQUAL, "==", None, 1),
            Token(TokenType.NUMBER, "5", 5.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(== 5.0 5.0)"
        self.assertEqual(expected, result)

        # Test inequality (!=) expression
        tokens = [
            Token(TokenType.NUMBER, "5", 5.0, 1),
            Token(TokenType.BANG_EQUAL, "!=", None, 1),
            Token(TokenType.NUMBER, "3", 3.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(!= 5.0 3.0)"
        self.assertEqual(expected, result)

    def test_comparison_expressions(self):
        # Test cases for comparison operators (>, >=, <, <=)
        # Each test verifies parsing expressions like: 5 > 3, 5 >= 3, etc.
        comparison_operators = [
            (TokenType.GREATER, ">"),
            (TokenType.GREATER_EQUAL, ">="),
            (TokenType.LESS, "<"),
            (TokenType.LESS_EQUAL, "<="),
        ]

        for op_type, op_lexeme in comparison_operators:
            tokens = [
                Token(TokenType.NUMBER, "5", 5.0, 1),
                Token(op_type, op_lexeme, None, 1),
                Token(TokenType.NUMBER, "3", 3.0, 1),
                Token(TokenType.SEMICOLON, ";", None, 1),
                Token(TokenType.EOF, "", None, 1),
            ]
            parser = Parser(tokens)
            statements = parser.parse()

            self.assertEqual(1, len(statements))

            ast_printer = AstPrinter()
            result = ast_printer.print(statements)
            expected = f"({op_lexeme} 5.0 3.0)"
            self.assertEqual(expected, result)

    def test_variable_expressions(self):
        # Test accessing a variable
        tokens = [
            Token(TokenType.IDENTIFIER, "someVar", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "someVar"
        self.assertEqual(expected, result)

    def test_assignment_expressions(self):
        # Test assignment expression
        tokens = [
            Token(TokenType.IDENTIFIER, "x", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.NUMBER, "10", 10.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(= x 10.0)"
        self.assertEqual(expected, result)

        # Test chained assignment: a = b = 5
        tokens = [
            Token(TokenType.IDENTIFIER, "a", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.IDENTIFIER, "b", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.NUMBER, "5", 5.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(= a (= b 5.0))"
        self.assertEqual(expected, result)

    def test_print_statements(self):
        # Test parsing a simple 'print' statement with a string literal
        tokens = [
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"hello"', "hello", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(print hello)"
        self.assertEqual(expected, result)

    def test_var_declarations(self):
        # Test parsing a variable declaration with an explicit initializer (var x = 10;)
        tokens = [
            Token(TokenType.VAR, "var", None, 1),
            Token(TokenType.IDENTIFIER, "x", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.NUMBER, "10", 10.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(var x 10.0)"
        self.assertEqual(expected, result)

        # Test parsing a variable declaration without an initializer (var y;)
        tokens = [
            Token(TokenType.VAR, "var", None, 1),
            Token(TokenType.IDENTIFIER, "y", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(var y)"
        self.assertEqual(expected, result)

    def test_block_statements(self):
        # Test simple block
        tokens = [
            Token(TokenType.LEFT_BRACE, "{", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"block"', "block", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.RIGHT_BRACE, "}", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(block (print block))"
        self.assertEqual(expected, result)

        # Test nested blocks
        tokens = [
            Token(TokenType.LEFT_BRACE, "{", None, 1),
            Token(TokenType.LEFT_BRACE, "{", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"nested"', "nested", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.RIGHT_BRACE, "}", None, 1),
            Token(TokenType.RIGHT_BRACE, "}", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(block (block (print nested)))"
        self.assertEqual(expected, result)

    def test_if_statements(self):
        # Test basic if statement without else
        tokens = [
            Token(TokenType.IF, "if", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"then branch"', "then branch", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(if true (print then branch))"
        self.assertEqual(expected, result)

        # Test if-else statement
        tokens = [
            Token(TokenType.IF, "if", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"then branch"', "then branch", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.ELSE, "else", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"else branch"', "else branch", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(if false (print then branch) (print else branch))"
        self.assertEqual(expected, result)

        # Test if with block statement
        tokens = [
            Token(TokenType.IF, "if", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.LEFT_BRACE, "{", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"block"', "block", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.RIGHT_BRACE, "}", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(if true (block (print block)))"
        self.assertEqual(expected, result)

        # Test nested if statements
        tokens = [
            Token(TokenType.IF, "if", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.IF, "if", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"inner"', "inner", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(if true (if false (print inner)))"
        self.assertEqual(expected, result)

    def test_logical_expressions(self):
        # Test 'and' logical operator
        tokens = [
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.AND, "and", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(and true false)"
        self.assertEqual(expected, result)

        # Test 'or' logical operator
        tokens = [
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.OR, "or", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(or false true)"
        self.assertEqual(expected, result)

        # Test precedence - 'and' binds tighter than 'or'
        tokens = [
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.OR, "or", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.AND, "and", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(or false (and true false))"
        self.assertEqual(expected, result)

        # Test complex logical expression with parentheses
        tokens = [
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.AND, "and", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.OR, "or", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(or (group (and true false)) true)"
        self.assertEqual(expected, result)

    def test_while_statements(self):
        # Test basic while loop
        tokens = [
            Token(TokenType.WHILE, "while", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.TRUE, "true", True, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"loop body"', "loop body", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(while true (print loop body))"
        self.assertEqual(expected, result)

        # Test while loop with block statement
        tokens = [
            Token(TokenType.WHILE, "while", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.FALSE, "false", False, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.LEFT_BRACE, "{", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"never executes"', "never executes", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.RIGHT_BRACE, "}", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(while false (block (print never executes)))"
        self.assertEqual(expected, result)

        # Test while loop with logical condition
        tokens = [
            Token(TokenType.WHILE, "while", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.IDENTIFIER, "x", None, 1),
            Token(TokenType.LESS, "<", None, 1),
            Token(TokenType.NUMBER, "10", 10.0, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.IDENTIFIER, "x", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.IDENTIFIER, "x", None, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "1", 1.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(1, len(statements))

        result = ast_printer.print(statements)
        expected = "(while (< x 10.0) (= x (+ x 1.0)))"
        self.assertEqual(expected, result)

    def test_for_statements(self):
        # Test basic for loop with all three clauses
        # for (var i = 0; i < 5; i = i + 1) print i;
        tokens = [
            Token(TokenType.FOR, "for", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.VAR, "var", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.NUMBER, "0", 0.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.LESS, "<", None, 1),
            Token(TokenType.NUMBER, "5", 5.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "1", 1.0, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)

        # The for loop should be desugared to a block with:
        # 1. var declaration initializer
        # 2. while loop with condition and a block containing:
        #    a. the body (print i)
        #    b. the increment (i = i + 1)
        expected = (
            "(block (var i 0.0) (while (< i 5.0) (block (print i) (= i (+ i 1.0)))))"
        )
        self.assertEqual(expected, result)

        # Test for loop with missing parts
        # for (;;) print "forever";
        tokens = [
            Token(TokenType.FOR, "for", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"forever"', "forever", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        result = ast_printer.print(statements)
        # Should be just a while(true) with the print statement
        expected = "(while true (print forever))"
        self.assertEqual(expected, result)

        # Test for loop with only condition
        # for (; i < 10;) print i;
        tokens = [
            Token(TokenType.FOR, "for", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.LESS, "<", None, 1),
            Token(TokenType.NUMBER, "10", 10.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        result = ast_printer.print(statements)
        # For loop with just condition - desugars to while loop
        expected = "(while (< i 10.0) (print i))"
        self.assertEqual(expected, result)

        # Test for loop with only initializer
        # for (var i = 0;;) print i;
        tokens = [
            Token(TokenType.FOR, "for", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.VAR, "var", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.NUMBER, "0", 0.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        result = ast_printer.print(statements)
        # For loop with just initializer - desugars to block with var declaration followed by while(true)
        expected = "(block (var i 0.0) (while true (print i)))"
        self.assertEqual(expected, result)

        # Test for loop with only increment
        # for (;; i = i + 1) print i;
        tokens = [
            Token(TokenType.FOR, "for", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "1", 1.0, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.IDENTIFIER, "i", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()

        result = ast_printer.print(statements)
        # For loop with just increment - desugars to while(true) with a block for body and increment
        expected = "(while true (block (print i) (= i (+ i 1.0))))"
        self.assertEqual(expected, result)

    def test_multiple_statements(self):
        # Test sequence of statements
        tokens = [
            Token(TokenType.VAR, "var", None, 1),
            Token(TokenType.IDENTIFIER, "x", None, 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.NUMBER, "1", 1.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.IDENTIFIER, "x", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]

        parser = Parser(tokens)
        statements = parser.parse()

        self.assertEqual(2, len(statements))

        ast_printer = AstPrinter()
        result = ast_printer.print(statements)
        expected = "(var x 1.0)\n(print x)"
        self.assertEqual(expected, result)

    def test_call(self):
        # Test parsing a simple function call with no arguments: foo()
        tokens = [
            Token(TokenType.IDENTIFIER, "foo", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1)
        ]
        parser = Parser(tokens)
        expr = parser.expression()
        self.assertIsInstance(expr, Call)
        self.assertIsInstance(expr.callee, Variable)
        self.assertEqual(expr.callee.name.lexeme, "foo")
        self.assertEqual(len(expr.arguments), 0)
        self.assertEqual(expr.paren.type, TokenType.RIGHT_PAREN)

        # Test parsing a function call with arguments: add(1, 2)
        tokens = [
            Token(TokenType.IDENTIFIER, "add", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.NUMBER, "1", 1.0, 1),
            Token(TokenType.COMMA, ",", None, 1),
            Token(TokenType.NUMBER, "2", 2.0, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1)
        ]
        parser = Parser(tokens)
        expr = parser.expression()
        self.assertIsInstance(expr, Call)
        self.assertIsInstance(expr.callee, Variable)
        self.assertEqual(expr.callee.name.lexeme, "add")
        self.assertEqual(len(expr.arguments), 2)
        self.assertIsInstance(expr.arguments[0], Literal)
        self.assertEqual(expr.arguments[0].value, 1.0)
        self.assertIsInstance(expr.arguments[1], Literal)
        self.assertEqual(expr.arguments[1].value, 2.0)

        # Test parsing nested function calls: outer(inner())
        tokens = [
            Token(TokenType.IDENTIFIER, "outer", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.IDENTIFIER, "inner", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.EOF, "", None, 1)
        ]
        parser = Parser(tokens)
        expr = parser.expression()
        self.assertIsInstance(expr, Call)
        self.assertEqual(expr.callee.name.lexeme, "outer")
        self.assertEqual(len(expr.arguments), 1)
        self.assertIsInstance(expr.arguments[0], Call)
        self.assertEqual(expr.arguments[0].callee.name.lexeme, "inner")
        self.assertEqual(len(expr.arguments[0].arguments), 0)
