import unittest
from app.parser import Parser
from app.ast_printer import AstPrinter
from app.token_type import TokenType
from app.token import Token
from app.error_handler import error_state


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
        self.assertEqual(result, expected)

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
