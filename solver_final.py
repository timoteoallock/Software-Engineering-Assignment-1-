from ast_nodes import (VarExpr, ShowExpr, ShowOneExpr, AssignmentExpr, TrueExpr, FalseExpr, OrExpr,
                       AndExpr, VariableExpr, NotExpr)

class Solver:
    def __init__(self, tree) :         

        self.all_declared_vars = []  
        self.ast = tree

    def solve(self):
        """Process each instruction in the AST."""
        declared_vars = []
        assigned_vars = {}

        for instruction in self.ast.instructions:
            if isinstance(instruction, VarExpr):
                self._declare_variables(instruction, declared_vars)
            elif isinstance(instruction, AssignmentExpr):
                self._assign_variable(instruction, declared_vars, assigned_vars)
            elif isinstance(instruction, (ShowExpr, ShowOneExpr)):
                self._process_show_instruction(instruction, declared_vars, assigned_vars)

    def _declare_variables(self, instruction, declared_vars):
        """Handle variable declarations."""
        for var in instruction.vars_list:
            if var in declared_vars:
                raise Exception(f"Variable '{var}' is declared more than once.")
            declared_vars.append(var)
            self.all_declared_vars.append(var)
            
    def _validate_expression(self, node, declared_vars, assigned_vars):
        """Validate that all variables in the expression are declared or assigned."""
        if isinstance(node, VariableExpr):
            var_name = node.identifier
            if var_name not in assigned_vars and var_name not in declared_vars:
                raise Exception(f"Undefined variable '{var_name}' used in expression.")
        elif isinstance(node, NotExpr):
            self._validate_expression(node.expression, declared_vars, assigned_vars)
        elif isinstance(node, (AndExpr, OrExpr)):
            self._validate_expression(node.left_expr, declared_vars, assigned_vars)
            self._validate_expression(node.right_expr, declared_vars, assigned_vars)
        elif isinstance(node, (TrueExpr, FalseExpr)):
            pass
        else:
            raise Exception(f"Unknown expression type: {type(node)}")

    def _assign_variable(self, instruction, declared_vars, assigned_vars):
        """Handle variable assignments."""
        var_name = instruction.var_name
        if var_name in declared_vars or var_name in assigned_vars:
            raise Exception(f"Identifier '{var_name}' has already been declared or assigned.")
        self._validate_expression(instruction.expression, declared_vars, assigned_vars)
        assigned_vars[var_name] = instruction.expression

    def _process_show_instruction(self, instruction, declared_vars, assigned_vars):
        """Handle 'show' and 'show_ones' instructions with pruning and sorting."""
        show_option = 'show' if isinstance(instruction, ShowExpr) else 'show_ones'
        show_ones_only = True  if show_option == 'show_ones' else False 
        output_vars = instruction.vars_list

        for variable in output_vars:
            if variable not in assigned_vars:
                raise Exception(
                    f"Variable '{variable}' was not assigned to an expression.")

        base_vars_list = declared_vars.copy()
        assigned_vars_copy = assigned_vars.copy()



        initial_assignment = {}
        results = []  # List to collect results as tuples (binary_value, result_line)
        count = 0  # To keep track of the number of displayed rows

        # Initialize caches
        eval_cache = {}
        possible_values_cache = {}

        # Start evaluation of nodes 

        def eval_expression(var_name, assignment_items):
            """Evaluate an expression for a given variable assignment using self-managed cache."""
            cache_key = (var_name, assignment_items)
            if cache_key in eval_cache:
                return eval_cache[cache_key]

            assignment = dict(assignment_items)
            if var_name in assigned_vars_copy:
                expr = assigned_vars_copy[var_name]
                result = eval_expr_node(expr, assignment)
                eval_cache[cache_key] = result
                return result
            else:
                raise Exception(f"Undefined variable '{var_name}' used in evaluation.")

        def eval_expr_node(node, assignment, memo=None):
            """Recursively evaluate an expression node with short-circuiting."""
            if memo is None:
                memo = {}

            node_id = id(node)
            if node_id in memo:
                return memo[node_id]

            if isinstance(node, AndExpr):
                left_val = eval_expr_node(node.left_expr, assignment, memo)
                if not left_val:
                    result = False  
                else:
                    result = eval_expr_node(node.right_expr, assignment, memo)

            elif isinstance(node, OrExpr):
                left_val = eval_expr_node(node.left_expr, assignment, memo)
                if left_val:
                    result = True  
                else:
                    result = eval_expr_node(node.right_expr, assignment, memo)


            elif isinstance(node, VariableExpr):
                var_name = node.identifier
                if var_name in assignment:
                    result = bool(assignment[var_name])
                else:
                    result = eval_expression(var_name, frozenset(assignment.items()))
            elif isinstance(node, NotExpr):
                result = not eval_expr_node(node.expression, assignment, memo)
            elif isinstance(node, TrueExpr):
                result = True
            elif isinstance(node, FalseExpr):
                result = False
            else:
                raise Exception(f"Expression not admissible: {type(node)}")

            memo[node_id] = result
            return result
        
    

        def possible_expr_values(expr, assignment_items, memo=None):

            if memo is None:
                memo = {}

            cache_key = (id(expr), assignment_items)
            if cache_key in possible_values_cache:
                return possible_values_cache[cache_key]
            if isinstance(expr, str):
                result = possible_var_values(expr, assignment_items, memo)

            elif isinstance(expr, AndExpr):
                left_vals = possible_expr_values(expr.left_expr, assignment_items, memo)
                if left_vals == {False}:
                    result = {False}
                else:
                    right_vals = possible_expr_values(expr.right_expr, assignment_items, memo)
                    result = {l and r for l in left_vals for r in right_vals}

            elif isinstance(expr, OrExpr):
                left_vals = possible_expr_values(expr.left_expr, assignment_items, memo)
                if left_vals == {True}:
                    result = {True}
                else:
                    right_vals = possible_expr_values(expr.right_expr, assignment_items, memo)
                    result = {l or r for l in left_vals for r in right_vals}

            elif isinstance(expr, VariableExpr):
                result = possible_var_values(expr.identifier, assignment_items, memo)
                
            elif isinstance(expr, NotExpr):
                sub_values = possible_expr_values(expr.expression, assignment_items, memo)
                result = {not v for v in sub_values}

            elif isinstance(expr, TrueExpr):
                result = {True}
            elif isinstance(expr, FalseExpr):
                result = {False}
            else:
                raise Exception(f"Unknown expression type: {type(expr)}")

            possible_values_cache[cache_key] = result
            return result


        def possible_var_values(var_name, assignment_items, memo):

            cache_key = (var_name, assignment_items)
            if cache_key in possible_values_cache:
                return possible_values_cache[cache_key]

            assignment = dict(assignment_items)
            if var_name in assignment:
                result = {bool(assignment[var_name])}
            elif var_name in assigned_vars_copy:
                expr = assigned_vars_copy[var_name]
                result = possible_expr_values(expr, assignment_items, memo)
            elif var_name in self.all_declared_vars:
                result = {True, False}
            else:
                raise Exception(f"Undefined variable '{var_name}' used in expression.")

            possible_values_cache[cache_key] = result
            return result

        def validate_output(assignment):
            """Check if any of the output expressions can still be True given the current assignment."""
            assignment_items = frozenset(assignment.items())
            for var in output_vars:
                possible_values = possible_expr_values(assigned_vars_copy[var], assignment_items)
                if True in possible_values:
                    return True
            return False

        def collect_results(assignment):
            """Collect evaluated expressions into the results list."""
            nonlocal count
            assignment_items = frozenset(assignment.items())
            output_values = [eval_expression(var, assignment_items) for var in output_vars]

            if show_ones_only and not any(output_values):
                return

            input_vals = [assignment[var] for var in base_vars_list]
            output_vals_str = ' '.join(str(int(val)) for val in output_values)
            result_line = ' '.join(str(bit) for bit in input_vals) + ' | ' + output_vals_str

            # Compute binary value for sorting
            binary_value = 0
            for bit in input_vals:
                binary_value = (binary_value << 1) | bit

            results.append((binary_value, result_line))
            count += 1

        def backtrack(variables, assignment):
            """Recursively assign truth values to variables, with pruning."""
            nonlocal count

            if len(assignment) == len(variables):
                collect_results(assignment)
                return

            var = variables[len(assignment)]
            for value in [1, 0]:  # Try 1 first for better pruning
                assignment[var] = value


                if show_ones_only and not validate_output(assignment):
                    assignment.pop(var)
                    continue

                backtrack(variables, assignment)

                assignment.pop(var)

        # Start recursion with base_vars_list
        backtrack(base_vars_list, initial_assignment)

        # Sort results based on binary value
        results.sort(key=lambda x: x[0])

        # Now print the results all at once
        for _, result_line in results:
            print(result_line)

        print()


