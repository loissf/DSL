import nodes
import context
import values

from nodes      import *
from context    import *
from values     import *

from tokens     import TypeGroups
from errors     import TypeError

class Interpreter:
    
    # Each visit method returns either a value or the result of another visit method
    # meaning the interpreter goes down the tree until it finds a value

    # Method to fetch a node in its visit_Name method
    def visit(self, node, context):
        method = getattr(self, f'visit_{type(node).__name__}')
        return method(node, context)

    def visit_NoneType(self, node, context):
        return None         # A visit to this node probably means something went wrong, otherwise Nonetype value should be wrapped in a Null type

    def visit_IntegerNode(self, node, context):
        return Integer(node.value)

    def visit_FloatNode(self, node, context):
        return Float(node.value)

    def visit_StringNode(self, node, context):
        return String(node.value)

    def visit_BooleanNode(self, node, context):
        return Boolean(node.value)
    
    def visit_VoidNode(self, node, context):
        return Null()

    def visit_AttributeAssingNode(self, node, context):
        object_value = self.visit(node.object_value, context)

        if not isinstance(object_value, Object):
            raise TypeError(f'{object_value} is not an object', node.position)

        var_name = node.attribute_node.var_name_token
        value = self.visit(node.value_node, context)

        self.visit(VarAssingNode(node.position, var_name, value), object_value.object_context)

    def visit_AttributeAccessNode(self, node, context):
        object_value = self.visit(node.object_value, context)

        if not isinstance(object_value, Object):
            raise TypeError(f'{object_value} is not an object', node.position)

        attribute_value = self.visit(node.attribute_node, object_value.object_context)
        
        if attribute_value == None:
            raise TypeError(f'{node.attribute_node.var_name_token.value} is not defined', node.position)

        return attribute_value

    def visit_VarAccessNode(self, node, context):
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)
 
        if value == None:
            raise TypeError(f'{var_name} is not defined', node.position)

        return value

    def visit_VarAssingNode(self, node, context):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node, context) if not isinstance(node.value_node, Value) else node.value_node
        context.symbol_table.set(var_name, value)

        return Null()

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
        return Null()

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

        return Null()

    def visit_FuncDefNode(self, node, context):
        func_name = node.func_name_token.value if node.func_name_token else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]

        function = Function(func_name, body_node, arg_names, context)

        if node.func_name_token:
            context.symbol_table.set(func_name, function)

        return Null()

    def visit_TriggerDefNode(self, node, context):
        trigger_list = context.get_root_context().symbol_table.parent.get('@triggers', True)
    
        event = self.visit(node.event, context)

        args = []
        if event == 0: # on_message TODO: constant values
            args = ['message']
        elif event == 1:
            pass       # on_event   TODO: other event types in this pattern
        else:
            pass
        
        function = Function('@trigger_function', node.body_node, args)

        trigger = Trigger(event, function, context)
        trigger_list.appendElement(trigger)

        return Null()

    def visit_ClassDefNode(self, node, context):
        class_name = node.class_name_token.value if node.class_name_token else None
        body_node = node.body_node
        
        new_class = Class(class_name, body_node)

        if node.class_name_token:
            context.symbol_table.set(class_name, new_class)
        
        return Null()

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
        right = self.visit(node.right_node, context)
        left = self.visit(node.left_node, context)
        op_token = node.op_token

        try:
            
            result = None

            # ARITHMETIC OPERATIONS
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

            # COMPARATION OPERATIONS
            elif op_token.type == TokenType.DOUBLE_EQUALS:
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

            # LOGIC OPERATIONS
            elif op_token.matches(TokenType.KEYWORD, 'and'):
                result = left.value and right.value
            elif op_token.matches(TokenType.KEYWORD, 'or'):
                result = left.value or right.value

            # Wrapping the result in the corresponding value type
            return Value(result).wrap()
            
        except Exception as e:
            raise TypeError(f"Runtime math error: {left.value}{op_token}{right.value} \n{e}", node.position)

# from values import Number, String, Boolean, Function, List, Callable, Class, Object
