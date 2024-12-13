from ast_nodes import (Program, VarExpr, ShowExpr, ShowOneExpr, AssignmentExpr, TrueExpr, FalseExpr, OrExpr,
                       AndExpr, VariableExpr, NotExpr)
class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.current_token = self.tokenizer.get_next_token()

    def error(self, message):
        raise Exception(f"Parser error: {message}")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.tokenizer.get_next_token()
        else:
            self.error(f"Expected token {token_type}, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")

    def parse(self):
        instructions = []
        while self.current_token.type != 'EOF':
            instructions.append(self.instruction())
        return Program(instructions)

    def instruction(self):
        if self.current_token.type == 'VAR':
            return self.var_declaration()
        elif self.current_token.type == 'ID':
            return self.assignment()
        elif self.current_token.type == 'SHOW':
            return self.show_instruction()
        elif self.current_token.type == 'SHOW_ONES':
            return self.show_one_instruction()
        else:
            self.error(f"Not admissible token {self.current_token.type}")

    def var_declaration(self):
        self.eat('VAR')
        ids = self.id_list()
        self.eat('SEMICOLON')
        return VarExpr(ids)

    def assignment(self):
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('EQUAL')
        expr = self.expression()
        self.eat('SEMICOLON')
        return AssignmentExpr(var_name, expr)

    def show_instruction(self):
        
        self.eat('SHOW')
        vars_list = self.id_list()
        self.eat('SEMICOLON')
        return ShowExpr(vars_list)
    
    def show_one_instruction(self):
        
        self.eat('SHOW_ONES')
        vars_list = self.id_list()
        self.eat('SEMICOLON')
        return ShowOneExpr(vars_list)

    def id_list(self):
        ids = [self.current_token.value]
        self.eat('ID')
        while self.current_token.type == 'ID':
            ids.append(self.current_token.value)
            self.eat('ID')
        return ids
    
    def expression(self):

        if self.current_token.type == 'NOT':
            self.eat('NOT')
            expr = self.paren_expr()
            expr = NotExpr(expr)
        else:
            expr = self.paren_expr()

        while self.current_token.type in ('AND', 'OR'):
            operator = self.current_token.type
            self.eat(operator)
            right = self.paren_expr()

            if operator == 'AND':
                expr = AndExpr(expr, right)
            elif operator == 'OR':
                expr = OrExpr(expr, right)

        return expr

    def paren_expr(self):
        if self.current_token.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.expression()
            self.eat('RPAREN')
            return expr
        elif self.current_token.type == 'TRUE':
            self.eat('TRUE')
            return TrueExpr()
        elif self.current_token.type == 'FALSE':
            self.eat('FALSE')
            return FalseExpr()
        elif self.current_token.type == 'ID':
            var_name = self.current_token.value
            self.eat('ID')
            return VariableExpr(var_name)
        else:
            self.error(f"Starting expression is not one of the following: (identifier, 'True', 'False', or '(' )")


