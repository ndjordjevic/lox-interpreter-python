from .expr import Visitor as ExprVisitor, Variable, Get, Expr
from .stmt import Visitor as StmtVisitor, Stmt
from .token import Token


class AstPrinter(ExprVisitor, StmtVisitor):
    def print(self, obj):
        if isinstance(obj, list):
            result = []
            for item in obj:
                if item is not None:
                    result.append(item.accept(self))
            return "\n".join(result)

        return obj.accept(self) if obj is not None else ""

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
        return self.parenthesize2("=", expr.name.lexeme, expr.value)

    def visit_logical_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_call_expr(self, expr):
        args = [expr.callee] + list(expr.arguments)
        return self.parenthesize("call", *args)

    def visit_get_expr(self, expr):
        return self.parenthesize2(".", expr.object, expr.name.lexeme)

    def visit_set_expr(self, expr):
        get_expr = self.parenthesize2(".", expr.object, expr.name.lexeme)
        return self.parenthesize2("=", get_expr, expr.value)

    def visit_super_expr(self, expr):
        return self.parenthesize2("super", expr.method)

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
        if stmt.else_branch is None:
            return self.parenthesize("if", stmt.condition, stmt.then_branch)
        return self.parenthesize(
            "if", stmt.condition, stmt.then_branch, stmt.else_branch
        )

    def visit_while_stmt(self, stmt):
        return self.parenthesize("while", stmt.condition, stmt.body)

    def visit_function_stmt(self, stmt):
        params = " ".join(param.lexeme for param in stmt.params)
        body_strs = []
        for s in stmt.body:
            if s is not None:
                body_strs.append(s.accept(self))
        return f"(fun {stmt.name.lexeme} ({params}) {' '.join(body_strs)})"

    def visit_return_stmt(self, stmt):
        if stmt.value is not None:
            return self.parenthesize("return", stmt.value)
        return "(return)"

    def visit_class_stmt(self, stmt):
        parts = [f"(class {stmt.name.lexeme}"]

        if stmt.superclass is not None:
            parts.append(" < ")
            parts.append(stmt.superclass.accept(self))

        for method in stmt.methods:
            parts.append(" ")
            parts.append(method.accept(self))

        parts.append(")")
        return "".join(parts)

    def parenthesize(self, name, *exprs):
        parts = [f"({name}"]
        for expr in exprs:
            parts.append(" ")
            parts.append(expr.accept(self))
        parts.append(")")
        return "".join(parts)

    def parenthesize2(self, name, *parts):
        """Like parenthesize but handles a wider range of types."""
        result = [f"({name}"]
        self._transform(result, parts)
        result.append(")")
        return "".join(result)

    def _transform(self, result, parts):
        """Transform various types into their string representations."""

        for part in parts:
            result.append(" ")
            if isinstance(part, Expr):
                result.append(part.accept(self))
            elif isinstance(part, Stmt):
                result.append(part.accept(self))
            elif isinstance(part, Token):
                result.append(part.lexeme)
            elif isinstance(part, list):
                self._transform(result, part)
            else:
                result.append(str(part))
