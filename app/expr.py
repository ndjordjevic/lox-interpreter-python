class Visitor:
    def visit_binary_expr(self, binary):  # Renamed from visit_binary
        pass

    def visit_grouping_expr(self, grouping):  # Renamed from visit_grouping
        pass

    def visit_literal_expr(self, literal):  # Renamed from visit_literal
        pass

    def visit_unary_expr(self, unary):  # Renamed from visit_unary
        pass

    def visit_variable_expr(self, variable):  # New method for Variable
        pass

    def visit_assign_expr(self, assign):  # New method for Assign
        pass


class Expr:
    def accept(self, visitor):
        pass


class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)  # Updated to match renamed method


class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)  # Updated to match renamed method


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)  # Updated to match renamed method


class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)
