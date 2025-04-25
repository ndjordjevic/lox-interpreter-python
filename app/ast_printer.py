from .expr import Visitor as ExprVisitor, Variable
from .stmt import Visitor as StmtVisitor


class AstPrinter(ExprVisitor, StmtVisitor):
    def print(self, obj):
        if isinstance(obj, list):
            result = []
            for item in obj:
                if item is not None:
                    result.append(item.accept(self))
            return "\n".join(result)

        # Handle individual expressions
        return obj.accept(self) if obj is not None else ""

    # Expression visitors
    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr):
        if isinstance(expr.value, bool):
            return "true" if expr.value else "false"
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr):
        return expr.name.lexeme

    def visit_assign_expr(self, expr):
        return self.parenthesize("=", Variable(expr.name), expr.value)

    def visit_logical_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    # Statement visitors
    def visit_expression_stmt(self, stmt):
        return stmt.expression.accept(self)

    def visit_print_stmt(self, stmt):
        return self.parenthesize("print", stmt.expression)

    def visit_var_stmt(self, stmt):
        if stmt.initializer is not None:
            return self.parenthesize("var", Variable(stmt.name), stmt.initializer)
        return self.parenthesize("var", Variable(stmt.name))

    def visit_block_stmt(self, stmt):
        result = ["(block"]
        for statement in stmt.statements:
            if statement is not None:
                result.append(" " + statement.accept(self))
        result.append(")")
        return "".join(result)

    def visit_if_stmt(self, stmt):
        # Handle if without else
        if stmt.else_branch is None:
            return self.parenthesize("if", stmt.condition, stmt.then_branch)
        # Handle if with else
        return self.parenthesize(
            "if", stmt.condition, stmt.then_branch, stmt.else_branch
        )

    def visit_while_stmt(self, stmt):
        return self.parenthesize("while", stmt.condition, stmt.body)

    def parenthesize(self, name, *exprs):
        builder = []
        builder.append(f"({name}")
        for expr in exprs:
            builder.append(" ")
            builder.append(expr.accept(self))
        builder.append(")")
        return "".join(builder)
