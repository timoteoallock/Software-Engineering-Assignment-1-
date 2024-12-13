class AST:
    pass

class TrueExpr(AST):
    pass

class FalseExpr(AST):
    pass
        
class NotExpr(AST):
    def __init__(self, expression):
        self.expression = expression

class ParenExpr(AST):
    def __init__(self, expr):
        self.expr = expr

class SimpleExpr(AST): 
    def __init__(self, s_expr): 
        self.simple_expr = s_expr

class Program(AST):
    def __init__(self, instructions):
        self.instructions = instructions 

class VarExpr(AST): 
    def __init__(self, var_id):
        self.vars_list = var_id

class AssignmentExpr(AST):
    def __init__(self, var_name, expression):
        self.var_name = var_name
        self.expression = expression

class ShowExpr(AST):
    def __init__(self, vars_list):
        self.vars_list = vars_list


class ShowOneExpr(AST):
    def __init__(self, vars_list):
        self.vars_list = vars_list


class VariableExpr(AST):
    def __init__(self, identifier):
        self.identifier = identifier


class AndExpr(AST):
    def __init__(self, left, right):
        self.left_expr = left
        self.right_expr = right

class OrExpr(AST):
    def __init__(self, left, right):
        self.left_expr = left
        self.right_expr = right
