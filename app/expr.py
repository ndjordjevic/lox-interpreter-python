class Visitor:
    def visit_binary_expr(self, binary):
        pass

    def visit_grouping_expr(self, grouping):
        pass

    def visit_literal_expr(self, literal):
        pass

    def visit_unary_expr(self, unary):
        pass

    def visit_variable_expr(self, variable):
        pass

    def visit_assign_expr(self, assign):
        pass

    def visit_logical_expr(self, logical):
        pass

    def visit_call_expr(self, call):
        pass

    def visit_get_expr(self, get):
        pass

    def visit_set_expr(self, set):
        pass

    def visit_this_expr(self, this):
        pass

    def visit_super_expr(self, super_expr):
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
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


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


class Logical(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)


class Call(Expr):
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call_expr(self)


class Get(Expr):
    def __init__(self, object, name):
        self.object = object
        self.name = name

    def accept(self, visitor):
        return visitor.visit_get_expr(self)


class Set(Expr):
    def __init__(self, object, name, value):
        self.object = object
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_set_expr(self)


class This(Expr):
    def __init__(self, keyword):
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visit_this_expr(self)


class Super(Expr):
    def __init__(self, keyword, method):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor):
        return visitor.visit_super_expr(self)

    def __str__(self):
        return f"Super({self.keyword}, {self.method})"
