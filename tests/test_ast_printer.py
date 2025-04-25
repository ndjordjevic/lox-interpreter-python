import unittest
from app.ast_printer import AstPrinter
from app.expr import Binary, Unary, Literal, Grouping, Variable, Assign, Logical
from app.stmt import Expression, Print, Var, Block, If, While
from app.token import Token
from app.token_type import TokenType


class TestAstPrinter(unittest.TestCase):
    def setUp(self):
        self.printer = AstPrinter()

    def test_literal(self):
        # Tests printing of different literal values (numbers, booleans, nil)
        self.assertEqual(self.printer.print(Literal(123)), "123")
        self.assertEqual(self.printer.print(Literal(True)), "true")
        self.assertEqual(self.printer.print(Literal(False)), "false")
        self.assertEqual(self.printer.print(Literal(None)), "nil")

    def test_unary(self):
        # Tests printing of unary negation expression (-123)
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        expr = Unary(minus_token, Literal(123))
        self.assertEqual(self.printer.print(expr), "(- 123)")

    def test_binary(self):
        # Tests printing of binary addition expression (1 + 2)
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        expr = Binary(Literal(1), plus_token, Literal(2))
        self.assertEqual(self.printer.print(expr), "(+ 1 2)")

    def test_grouping(self):
        # Tests printing of parenthesized grouping expression ((45.67))
        expr = Grouping(Literal(45.67))
        self.assertEqual(self.printer.print(expr), "(group 45.67)")

    def test_complex_expression(self):
        # Tests printing of complex nested expression (-123 * (45.67))
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        star_token = Token(TokenType.STAR, "*", None, 1)
        expr = Binary(
            Unary(minus_token, Literal(123)), star_token, Grouping(Literal(45.67))
        )
        self.assertEqual(self.printer.print(expr), "(* (- 123) (group 45.67))")

    def test_variable(self):
        # Tests printing of variable reference expression (myVar)
        var_token = Token(TokenType.IDENTIFIER, "myVar", None, 1)
        expr = Variable(var_token)
        self.assertEqual(self.printer.print(expr), "myVar")

    def test_assign(self):
        # Tests printing of assignment expression (myVar = 42)
        var_token = Token(TokenType.IDENTIFIER, "myVar", None, 1)
        expr = Assign(var_token, Literal(42))
        self.assertEqual(self.printer.print(expr), "(= myVar 42)")

        # Tests printing of complex assignment (myVar = myVar + 1)
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        expr = Assign(var_token, Binary(Variable(var_token), plus_token, Literal(1)))
        self.assertEqual(self.printer.print(expr), "(= myVar (+ myVar 1))")

    def test_expression_stmt(self):
        # Tests printing of simple expression statement (42;)
        expr = Literal(42)
        stmt = Expression(expr)
        self.assertEqual(self.printer.print(stmt), "42")

        # Tests printing of complex expression statement (1 + 2;)
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        expr = Binary(Literal(1), plus_token, Literal(2))
        stmt = Expression(expr)
        self.assertEqual(self.printer.print(stmt), "(+ 1 2)")

    def test_print_stmt(self):
        # Tests printing of print statement with string literal (print "hello";)
        expr = Literal("hello")
        stmt = Print(expr)
        self.assertEqual(self.printer.print(stmt), "(print hello)")

        # Tests printing of print statement with complex expression (print -123;)
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        expr = Unary(minus_token, Literal(123))
        stmt = Print(expr)
        self.assertEqual(self.printer.print(stmt), "(print (- 123))")

    def test_var_stmt(self):
        # Tests printing of variable declaration without initializer (var myVar;)
        var_token = Token(TokenType.IDENTIFIER, "myVar", None, 1)
        stmt = Var(var_token, None)
        self.assertEqual(self.printer.print(stmt), "(var myVar)")

        # Tests printing of variable declaration with initializer (var myVar = 42;)
        stmt = Var(var_token, Literal(42))
        self.assertEqual(self.printer.print(stmt), "(var myVar 42)")

    def test_block_stmt(self):
        # Tests printing of empty block statement ({})
        stmt = Block([])
        self.assertEqual(self.printer.print(stmt), "(block)")

        # Tests printing of block with multiple statements ({var x = 10; print x;})
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        var_stmt = Var(var_token, Literal(10))

        print_stmt = Print(Variable(var_token))

        stmt = Block([var_stmt, print_stmt])
        self.assertEqual(self.printer.print(stmt), "(block (var x 10) (print x))")

    def test_if_stmt(self):
        # Test if statement without else (if (true) print "then";)
        condition = Literal(True)
        then_branch = Print(Literal("then"))
        stmt = If(condition, then_branch, None)
        self.assertEqual(self.printer.print(stmt), "(if true (print then))")

        # Test if-else statement (if (false) print "then"; else print "else";)
        condition = Literal(False)
        then_branch = Print(Literal("then"))
        else_branch = Print(Literal("else"))
        stmt = If(condition, then_branch, else_branch)
        self.assertEqual(
            self.printer.print(stmt), "(if false (print then) (print else))"
        )

        # Test if with complex condition (if (x > 5) print "greater";)
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        greater_token = Token(TokenType.GREATER, ">", None, 1)
        condition = Binary(Variable(var_token), greater_token, Literal(5))
        then_branch = Print(Literal("greater"))
        stmt = If(condition, then_branch, None)
        self.assertEqual(self.printer.print(stmt), "(if (> x 5) (print greater))")

        # Test if with block body (if (true) { print "block"; })
        condition = Literal(True)
        then_branch = Block([Print(Literal("block"))])
        stmt = If(condition, then_branch, None)
        self.assertEqual(self.printer.print(stmt), "(if true (block (print block)))")

    def test_logical_expr(self):
        # Test 'and' logical expression (true and false)
        and_token = Token(TokenType.AND, "and", None, 1)
        expr = Logical(Literal(True), and_token, Literal(False))
        self.assertEqual(self.printer.print(expr), "(and true false)")

        # Test 'or' logical expression (false or true)
        or_token = Token(TokenType.OR, "or", None, 1)
        expr = Logical(Literal(False), or_token, Literal(True))
        self.assertEqual(self.printer.print(expr), "(or false true)")

        # Test complex logical expression (true and false or true)
        expr = Logical(
            Logical(Literal(True), and_token, Literal(False)), or_token, Literal(True)
        )
        self.assertEqual(self.printer.print(expr), "(or (and true false) true)")

        # Test logical with variables (x and y)
        x_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        y_token = Token(TokenType.IDENTIFIER, "y", None, 1)
        expr = Logical(Variable(x_token), and_token, Variable(y_token))
        self.assertEqual(self.printer.print(expr), "(and x y)")

        # Test logical with comparison (x > 5 or y < 10)
        greater_token = Token(TokenType.GREATER, ">", None, 1)
        less_token = Token(TokenType.LESS, "<", None, 1)
        expr = Logical(
            Binary(Variable(x_token), greater_token, Literal(5)),
            or_token,
            Binary(Variable(y_token), less_token, Literal(10))
        )
        self.assertEqual(self.printer.print(expr), "(or (> x 5) (< y 10))")

    def test_while_stmt(self):
        # Test basic while loop (while (true) print "loop";)
        condition = Literal(True)
        body = Print(Literal("loop"))
        stmt = While(condition, body)
        self.assertEqual(self.printer.print(stmt), "(while true (print loop))")

        # Test while with complex condition (while (x < 10) print x;)
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        less_token = Token(TokenType.LESS, "<", None, 1)
        condition = Binary(Variable(var_token), less_token, Literal(10))
        body = Print(Variable(var_token))
        stmt = While(condition, body)
        self.assertEqual(self.printer.print(stmt), "(while (< x 10) (print x))")

        # Test while with block body (while (true) { print "block"; })
        condition = Literal(True)
        body = Block([Print(Literal("block"))])
        stmt = While(condition, body)
        self.assertEqual(self.printer.print(stmt), "(while true (block (print block)))")

        # Test while with logical condition (while (x > 0 and x < 10) print x;)
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        greater_token = Token(TokenType.GREATER, ">", None, 1)
        less_token = Token(TokenType.LESS, "<", None, 1)
        and_token = Token(TokenType.AND, "and", None, 1)
        condition = Logical(
            Binary(Variable(var_token), greater_token, Literal(0)),
            and_token,
            Binary(Variable(var_token), less_token, Literal(10))
        )
        body = Print(Variable(var_token))
        stmt = While(condition, body)
        self.assertEqual(self.printer.print(stmt), "(while (and (> x 0) (< x 10)) (print x))")

    def test_multiple_statements(self):
        # Tests printing of multiple statements in sequence (var x = 42; print x;)
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        stmt1 = Var(var_token, Literal(42))

        print_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        stmt2 = Print(Variable(print_token))

        statements = [stmt1, stmt2]
        self.assertEqual(self.printer.print(statements), "(var x 42)\n(print x)")


if __name__ == "__main__":
    unittest.main()
