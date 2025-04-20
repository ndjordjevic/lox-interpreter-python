import unittest
from app.ast_printer import AstPrinter
from app.expr import Binary, Unary, Literal, Grouping, Variable, Assign
from app.stmt import Expression, Print, Var, Block
from app.token import Token
from app.token_type import TokenType


class TestAstPrinter(unittest.TestCase):
    def setUp(self):
        self.printer = AstPrinter()

    def test_literal(self):
        self.assertEqual(self.printer.print(Literal(123)), "123")
        self.assertEqual(self.printer.print(Literal(True)), "true")
        self.assertEqual(self.printer.print(Literal(False)), "false")
        self.assertEqual(self.printer.print(Literal(None)), "nil")

    def test_unary(self):
        # Use a Token object for the operator
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        expr = Unary(minus_token, Literal(123))
        self.assertEqual(self.printer.print(expr), "(- 123)")

    def test_binary(self):
        # Use a Token object for the operator
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        expr = Binary(Literal(1), plus_token, Literal(2))
        self.assertEqual(self.printer.print(expr), "(+ 1 2)")

    def test_grouping(self):
        expr = Grouping(Literal(45.67))
        self.assertEqual(self.printer.print(expr), "(group 45.67)")

    def test_complex_expression(self):
        # Use Token objects for the operators
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        star_token = Token(TokenType.STAR, "*", None, 1)
        expr = Binary(Unary(minus_token, Literal(123)), star_token, Grouping(Literal(45.67)))
        self.assertEqual(self.printer.print(expr), "(* (- 123) (group 45.67))")
        
    def test_variable(self):
        # Test variable reference
        var_token = Token(TokenType.IDENTIFIER, "myVar", None, 1)
        expr = Variable(var_token)
        self.assertEqual(self.printer.print(expr), "myVar")
    
    def test_assign(self):
        # Test assignment expression
        var_token = Token(TokenType.IDENTIFIER, "myVar", None, 1)
        expr = Assign(var_token, Literal(42))
        self.assertEqual(self.printer.print(expr), "(= myVar 42)")
        
        # Test complex assignment
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        expr = Assign(var_token, Binary(Variable(var_token), plus_token, Literal(1)))
        self.assertEqual(self.printer.print(expr), "(= myVar (+ myVar 1))")

    # Add tests for statements
    def test_expression_stmt(self):
        # Expression statement just prints the expression
        expr = Literal(42)
        stmt = Expression(expr)
        self.assertEqual(self.printer.print(stmt), "42")
        
        # More complex expression statement
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        expr = Binary(Literal(1), plus_token, Literal(2))
        stmt = Expression(expr)
        self.assertEqual(self.printer.print(stmt), "(+ 1 2)")
    
    def test_print_stmt(self):
        # Print statement with a literal
        expr = Literal("hello")
        stmt = Print(expr)
        self.assertEqual(self.printer.print(stmt), "(print hello)")
        
        # Print statement with a complex expression
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        expr = Unary(minus_token, Literal(123))
        stmt = Print(expr)
        self.assertEqual(self.printer.print(stmt), "(print (- 123))")
    
    def test_var_stmt(self):
        # Variable declaration without initializer
        var_token = Token(TokenType.IDENTIFIER, "myVar", None, 1)
        stmt = Var(var_token, None)
        self.assertEqual(self.printer.print(stmt), "(var myVar)")
        
        # Variable declaration with initializer
        stmt = Var(var_token, Literal(42))
        self.assertEqual(self.printer.print(stmt), "(var myVar 42)")
    
    def test_block_stmt(self):
        # Empty block
        stmt = Block([])
        self.assertEqual(self.printer.print(stmt), "(block)")
        
        # Block with statements
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        var_stmt = Var(var_token, Literal(10))
        
        print_stmt = Print(Variable(var_token))
        
        stmt = Block([var_stmt, print_stmt])
        self.assertEqual(self.printer.print(stmt), "(block (var x 10) (print x))")
        
    def test_multiple_statements(self):
        # Test printing a list of statements
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        stmt1 = Var(var_token, Literal(42))
        
        print_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        stmt2 = Print(Variable(print_token))
        
        statements = [stmt1, stmt2]
        self.assertEqual(self.printer.print(statements), "(var x 42)\n(print x)")


if __name__ == "__main__":
    unittest.main()
