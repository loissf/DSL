from nodes import *
from context import SymbolTable, Context
from tokens import TypeGroups
from errors import TypeError

class Interpreter:
    
    # Each visit method returns either a value or the result of another visit method
    # meaning the interpreter goes down the tree until it finds a value

    # Method to fetch a node in its visit_Name method
    def visit(self, node, context):
        method = getattr(self, f'visit_{type(node).__name__}')
        return method(node, context)

    def visit_NumberNode(self, node, context):
        return Number(node.value)

    def visit_StringNode(self, node, context):
        return String(node.value)

    def visit_BooleanNode(self, node, context):
        return Boolean(node.value)

    def visit_VoidNode(self, node, context):
        return None
    # NOW A BUILT IN FUNCTION
    '''
    def visit_WriteNode(self, node, context):
        value = self.visit(node.value_node, context)
        print(value)
        return None
    '''
    def visit_VarAccessNode(self, node, context):
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if value == None:
            raise TypeError(f'{var_name} is not defined', node.position)

        return value

    def visit_VarAssingNode(self, node, context):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node, context)
        context.symbol_table.set(var_name, value)

        return None

    def visit_ListNode(self, node, context):
        elements = []

        for element_node in node.element_nodes:
            elements.append(self.visit(element_node, context))
        
        return List(elements)

    def visit_ListAccessNode(self, node, context):
        list_var = self.visit(node.list_node, context)
        index = self.visit(node.index_node, context)

        return list_var.getElement(index.value)
    
    def visit_ListAssingNode(self, node, context):
        list_var = self.visit(node.list_node, context)
        index = self.visit(node.index_node, context)
        value = self.visit(node.value_node, context)
        
        list_var.setElement(index.value, value)
        return None

    def visit_IfNode(self, node, context):
        condition_value = self.visit(node.condition, context)
        if condition_value == Boolean(True):
            if_case_value = self.visit(node.if_case, context)
            # return if_case_value
        elif node.else_case:
            else_case_value = self.visit(node.else_case, context)
            # return else_case_value
        else:
            pass

        return None

    def visit_FuncDefNode(self, node, context):
        func_name = node.func_name_token.value if node.func_name_token else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]

        function = Function(func_name, body_node, arg_names)

        if node.func_name_token:
            context.symbol_table.set(func_name, function)

        return None

    def visit_CallNode(self, node, context):
        args = []

        function = self.visit(node.func_node, context)
        if not isinstance(function, Callable):
            raise TypeError((f'{node.func_node} is not callable'), node.position)
        
        for arg_node in node.arg_nodes:
            args.append(self.visit(arg_node, context))

        return function.execute(args, context)
            
    def visit_UnaryOpNode(self, node, context):
        if node.op_token.type == TokenType.MINUS:
            value = self.visit(node.node, context).value
            result = -value
            return Number(result)
        if node.op_token.type.matches(TokenType.KEYWORD, 'not'):
            value = self.visit(node.node, context)
            result = not value
            return Boolean(result)

    def visit_BinOpNode(self, node, context):
        try:
            right = self.visit(node.right_node, context)
            left = self.visit(node.left_node, context)
            op_token = node.op_token
            
            if op_token.type in TypeGroups.ARITHMETIC_OP:
                
                result: float

                if op_token.type == TokenType.PLUS:
                    result = left.value + right.value
                elif op_token.type == TokenType.MINUS:
                    result = left.value - right.value
                elif op_token.type == TokenType.MULTIPLY:
                    result = left.value * right.value
                elif op_token.type == TokenType.DIVIDE:
                    if right.value == 0:
                        raise ZeroDivisionError("Division by zero", node.right_node.position)
                    result = left.value / right.value

                return Number(result)

            elif op_token.type in TypeGroups.COMPARATION_OP:
                
                result: bool

                if op_token.type == TokenType.DOUBLE_EQUALS:
                    result = left.value == right.value
                elif op_token.type == TokenType.NOT_EQUALS:
                    result = left.value != right.value
                elif op_token.type == TokenType.GREATER:
                    result = left.value > right.value
                elif op_token.type == TokenType.GREATER_EQUALS:
                    result = left.value >= right.value
                elif op_token.type == TokenType.LOWER:
                    result = left.value < right.value
                elif op_token.type == TokenType.LOWER_EQUALS:
                    result = left.value <= right.value

                return Boolean(result)

            elif op_token.matches(TokenType.KEYWORD, 'and'):
                result = left.value and right.value
                return Boolean(result)
            elif op_token.matches(TokenType.KEYWORD, 'or'):
                result = left.value or right.value
                return Boolean(result)

        except:
            raise TypeError("Runtime math error", node.position)

from values import Number, String, Boolean, Function, List, Callable
