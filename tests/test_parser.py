import unittest
from app.parser import Parser
from app.ast_printer import AstPrinter
from app.token_type import TokenType
from app.token import Token
from app.error_handler import error_state
from app.expr import Binary, Literal, Grouping, Unary, Variable, Assign
from app.stmt import Expression, Print, Var, Block


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
        stmt = statements[0]
        self.assertIsInstance(stmt, Expression)
        self.assertIsInstance(stmt.expression, Binary)
        self.assertEqual(TokenType.EQUAL_EQUAL, stmt.expression.operator.type)
        
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
        stmt = statements[0]
        self.assertIsInstance(stmt, Expression)
        self.assertIsInstance(stmt.expression, Binary)
        self.assertEqual(TokenType.BANG_EQUAL, stmt.expression.operator.type)
    
    def test_comparison_expressions(self):
        comparison_operators = [
            (TokenType.GREATER, ">"),
            (TokenType.GREATER_EQUAL, ">="),
            (TokenType.LESS, "<"),
            (TokenType.LESS_EQUAL, "<=")
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
            stmt = statements[0]
            self.assertIsInstance(stmt, Expression)
            self.assertIsInstance(stmt.expression, Binary)
            self.assertEqual(op_type, stmt.expression.operator.type)
    
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
        stmt = statements[0]
        self.assertIsInstance(stmt, Expression)
        self.assertIsInstance(stmt.expression, Variable)
        self.assertEqual("someVar", stmt.expression.name.lexeme)
    
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
        stmt = statements[0]
        self.assertIsInstance(stmt, Expression)
        self.assertIsInstance(stmt.expression, Assign)
        self.assertEqual("x", stmt.expression.name.lexeme)
        self.assertIsInstance(stmt.expression.value, Literal)
        
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
        stmt = statements[0]
        self.assertIsInstance(stmt, Expression)
        self.assertIsInstance(stmt.expression, Assign)
        self.assertEqual("a", stmt.expression.name.lexeme)
        self.assertIsInstance(stmt.expression.value, Assign)
        self.assertEqual("b", stmt.expression.value.name.lexeme)
    
    def test_print_statements(self):
        # Test print statement
        tokens = [
            Token(TokenType.PRINT, "print", None, 1),
            Token(TokenType.STRING, '"hello"', "hello", 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()
        
        self.assertEqual(1, len(statements))
        stmt = statements[0]
        self.assertIsInstance(stmt, Print)
        self.assertIsInstance(stmt.expression, Literal)
        self.assertEqual("hello", stmt.expression.value)
    
    def test_var_declarations(self):
        # Test variable declaration with initializer
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
        stmt = statements[0]
        self.assertIsInstance(stmt, Var)
        self.assertEqual("x", stmt.name.lexeme)
        self.assertIsInstance(stmt.initializer, Literal)
        
        # Test variable declaration without initializer
        tokens = [
            Token(TokenType.VAR, "var", None, 1),
            Token(TokenType.IDENTIFIER, "y", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(tokens)
        statements = parser.parse()
        
        self.assertEqual(1, len(statements))
        stmt = statements[0]
        self.assertIsInstance(stmt, Var)
        self.assertEqual("y", stmt.name.lexeme)
        self.assertIsNone(stmt.initializer)
    
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
        stmt = statements[0]
        self.assertIsInstance(stmt, Block)
        self.assertEqual(1, len(stmt.statements))
        self.assertIsInstance(stmt.statements[0], Print)
        
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
        outer_block = statements[0]
        self.assertIsInstance(outer_block, Block)
        self.assertEqual(1, len(outer_block.statements))
        inner_block = outer_block.statements[0]
        self.assertIsInstance(inner_block, Block)
    
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
        self.assertIsInstance(statements[0], Var)
        self.assertIsInstance(statements[1], Print)
        self.assertIsInstance(statements[1].expression, Variable)
