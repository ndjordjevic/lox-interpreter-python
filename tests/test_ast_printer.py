import unittest
from app.ast_printer import AstPrinter
from app.expr import Binary, Unary, Literal, Grouping, Variable, Assign, Logical, Call, Get, Set
from app.stmt import Expression, Print, Var, Block, If, While, Function, Return
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

    def test_call(self):
        # Tests printing of function call without arguments (foo())
        callee = Variable(Token(TokenType.IDENTIFIER, "foo", None, 1))
        paren = Token(TokenType.RIGHT_PAREN, ")", None, 1)
        expr = Call(callee, paren, [])
        self.assertEqual(self.printer.print(expr), "(call foo)")

        # Tests printing of function call with arguments (add(1, 2))
        callee = Variable(Token(TokenType.IDENTIFIER, "add", None, 1))
        paren = Token(TokenType.RIGHT_PAREN, ")", None, 1)
        args = [Literal(1), Literal(2)]
        expr = Call(callee, paren, args)
        self.assertEqual(self.printer.print(expr), "(call add 1 2)")

        # Tests printing of nested function calls (outer(inner()))
        inner_callee = Variable(Token(TokenType.IDENTIFIER, "inner", None, 1))
        inner_paren = Token(TokenType.RIGHT_PAREN, ")", None, 1)
        inner_call = Call(inner_callee, inner_paren, [])
        outer_callee = Variable(Token(TokenType.IDENTIFIER, "outer", None, 1))
        outer_paren = Token(TokenType.RIGHT_PAREN, ")", None, 1)
        expr = Call(outer_callee, outer_paren, [inner_call])
        self.assertEqual(self.printer.print(expr), "(call outer (call inner))")

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

    def test_function_stmt(self):
        # fun add(a, b) { print a; }
        name_token = Token(TokenType.IDENTIFIER, "add", None, 1)
        param_a = Token(TokenType.IDENTIFIER, "a", None, 1)
        param_b = Token(TokenType.IDENTIFIER, "b", None, 1)
        body_stmt = Print(Variable(param_a))
        stmt = Function(name_token, [param_a, param_b], [body_stmt])
        expected = "(fun add (a b) (print a))"
        self.assertEqual(self.printer.print(stmt), expected)

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
            Binary(Variable(y_token), less_token, Literal(10)),
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
            Binary(Variable(var_token), less_token, Literal(10)),
        )
        body = Print(Variable(var_token))
        stmt = While(condition, body)
        self.assertEqual(
            self.printer.print(stmt), "(while (and (> x 0) (< x 10)) (print x))"
        )

    def test_return_stmt_with_value(self):
        stmt = Return(
            Token(TokenType.RETURN, "return", None, 1),
            Literal(42.0)
        )
        self.assertEqual(self.printer.print(stmt), "(return 42.0)")

    def test_return_stmt_without_value(self):
        stmt = Return(
            Token(TokenType.RETURN, "return", None, 1),
            None
        )
        self.assertEqual(self.printer.print(stmt), "(return)")

    def test_return_stmt_with_expression(self):
        expr = Binary(
            Variable(Token(TokenType.IDENTIFIER, "x", None, 1)),
            Token(TokenType.PLUS, "+", None, 1),
            Literal(1.0)
        )
        stmt = Return(
            Token(TokenType.RETURN, "return", None, 1),
            expr
        )
        self.assertEqual(self.printer.print(stmt), "(return (+ x 1.0))")

    def test_multiple_statements(self):
        # Tests printing of multiple statements in sequence (var x = 42; print x;)
        var_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        stmt1 = Var(var_token, Literal(42))

        print_token = Token(TokenType.IDENTIFIER, "x", None, 1)
        stmt2 = Print(Variable(print_token))

        statements = [stmt1, stmt2]
        self.assertEqual(self.printer.print(statements), "(var x 42)\n(print x)")

    def test_get_expr(self):
        # Test simple property access (instance.property)
        instance = Variable(Token(TokenType.IDENTIFIER, "instance", None, 1))
        property_name = Token(TokenType.IDENTIFIER, "property", None, 1)
        expr = Get(instance, property_name)
        self.assertEqual(self.printer.print(expr), "(. instance property)")

        # Test nested property access (instance.property.subproperty)
        subproperty_name = Token(TokenType.IDENTIFIER, "subproperty", None, 1)
        nested_expr = Get(expr, subproperty_name)
        self.assertEqual(self.printer.print(nested_expr), "(. (. instance property) subproperty)")

        # Test property access on method call result (instance.method().property)
        method_name = Token(TokenType.IDENTIFIER, "method", None, 1)
        method_call = Call(Variable(method_name), Token(TokenType.RIGHT_PAREN, ")", None, 1), [])
        method_expr = Get(instance, method_name)
        method_call_expr = Call(method_expr, Token(TokenType.RIGHT_PAREN, ")", None, 1), [])
        property_expr = Get(method_call_expr, property_name)
        self.assertEqual(self.printer.print(property_expr), "(. (call (. instance method)) property)")

        # Test property access on literal value (42.property)
        literal = Literal(42)
        expr = Get(literal, property_name)
        self.assertEqual(self.printer.print(expr), "(. 42 property)")

        # Test property access on binary expression ((1 + 2).property)
        plus_token = Token(TokenType.PLUS, "+", None, 1)
        binary_expr = Binary(Literal(1), plus_token, Literal(2))
        expr = Get(binary_expr, property_name)
        self.assertEqual(self.printer.print(expr), "(. (+ 1 2) property)")

        # Test property access on unary expression (-42.property)
        minus_token = Token(TokenType.MINUS, "-", None, 1)
        unary_expr = Unary(minus_token, Literal(42))
        expr = Get(unary_expr, property_name)
        self.assertEqual(self.printer.print(expr), "(. (- 42) property)")

        # Test property access on grouping expression ((42).property)
        grouping_expr = Grouping(Literal(42))
        expr = Get(grouping_expr, property_name)
        self.assertEqual(self.printer.print(expr), "(. (group 42) property)")

        # Test property access on logical expression (true and false).property
        and_token = Token(TokenType.AND, "and", None, 1)
        logical_expr = Logical(Literal(True), and_token, Literal(False))
        expr = Get(logical_expr, property_name)
        self.assertEqual(self.printer.print(expr), "(. (and true false) property)")

        # Test property access with different property names
        property_names = ["x", "y", "z", "value", "data", "result"]
        for name in property_names:
            name_token = Token(TokenType.IDENTIFIER, name, None, 1)
            expr = Get(instance, name_token)
            self.assertEqual(self.printer.print(expr), f"(. instance {name})")

    def test_set_expr(self):
        # Test simple property assignment (instance.property = value)
        instance = Variable(Token(TokenType.IDENTIFIER, "instance", None, 1))
        property_name = Token(TokenType.IDENTIFIER, "property", None, 1)
        value = Literal(42)
        expr = Set(instance, property_name, value)
        self.assertEqual(self.printer.print(expr), "(= (. instance property) 42)")

        # Test nested property assignment (instance.property.subproperty = value)
        subproperty_name = Token(TokenType.IDENTIFIER, "subproperty", None, 1)
        nested_expr = Set(Get(instance, property_name), subproperty_name, value)
        self.assertEqual(self.printer.print(nested_expr), "(= (. (. instance property) subproperty) 42)")


if __name__ == "__main__":
    unittest.main()
