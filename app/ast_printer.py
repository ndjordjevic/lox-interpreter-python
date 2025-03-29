from app.expr import Visitor, Binary, Grouping, Literal, Unary


class AstPrinter(Visitor):
    def print(self, expr):
        if isinstance(expr, Literal):
            if expr.value is True:
                return "true"
            if expr.value is False:
                return "false"
            if expr.value is None:
                return "nil"
            return str(expr.value)
        return expr.accept(self)

    def visit_binary(self, binary):
        return self.parenthesize(binary.operator, binary.left, binary.right)

    def visit_grouping(self, grouping):
        return self.parenthesize("group", grouping.expression)

    def visit_literal(self, literal):
        if isinstance(literal.value, bool):
            return (
                "true" if literal.value else "false"
            )  # Ensure boolean literals are lowercase
        if literal.value is None:
            return "nil"
        return str(literal.value)

    def visit_unary(self, unary):
        # Ensure the operator is passed as a string
        return self.parenthesize(str(unary.operator), unary.right)

    def parenthesize(self, name, *exprs):
        builder = []
        builder.append(f"({name}")
        for expr in exprs:
            builder.append(" ")
            builder.append(expr.accept(self))
        builder.append(")")
        return "".join(builder)


# Temporary main function to see how it works
if __name__ == "__main__":
    expression = Binary(Unary("-", Literal(123)), "*", Grouping(Literal(45.67)))

    print(AstPrinter().print(expression))
