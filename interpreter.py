from nodes      import *
from values     import *

from context    import Context

from tokens     import TokenType

from lexer      import Lexer
from parser_    import Parser

from errors     import Error
from errors     import TypeErrorDsl, IndexErrorDsl

class Interpreter:

    # Each visit method returns either a value or the result of another visit method
    # meaning the interpreter goes down the tree until it finds a value

    # Method to fetch a node in its visit_Name method
    def visit(self, node, context: Context):
        method = getattr(self, f'visit_{type(node).__name__}')
        return method(node, context)

    def visit_NoneType(self, node, context: Context):
        return Null()         # A visit to this node probably means something went wrong

    def visit_IntegerNode(self, node: IntegerNode, context: Context):
        return Integer(node.value)

    def visit_FloatNode(self, node: FloatNode, context: Context):
        return Float(node.value)

    def visit_StringNode(self, node: StringNode, context: Context):
        return String(node.value)

    def visit_BooleanNode(self, node: BooleanNode, context: Context):
        return Boolean(node.value)

    def visit_VoidNode(self, node: VoidNode, context: Context):
        return Null()

    def visit_AttributeAssingNode(self, node: AttributeAssingNode, context: Context):
        object_value = self.visit(node.object_value, context)

        if not isinstance(object_value, Object):
            raise TypeErrorDsl(f'{object_value} is not an object', node.position)

        var_name = node.attribute_node.var_name_token.value

        value = self.visit(node.value_node, context)

        object_value.set(var_name, value)

        return Null()

    def visit_AttributeAccessNode(self, node: AttributeAccessNode, context: Context):
        object_value = self.visit(node.object_value, context)

        if not isinstance(object_value, Object):
            raise TypeErrorDsl(f'{object_value} is not an object', node.position)

        if isinstance(node.attribute_node, AttributeAccessNode):
            var_name = self.visit(node.attribute_node, context).var_name_token.value
        else:
            var_name = node.attribute_node.var_name_token.value

        attribute_value = object_value.get(var_name)

        if attribute_value == None:
            raise TypeErrorDsl(f'{node.attribute_node} is not defined', node.position)

        return attribute_value

    def visit_VarAccessNode(self, node: VarAccessNode, context: Context):
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if value == None:
            raise TypeErrorDsl(f'{var_name} is not defined', node.position)

        return value

    def visit_VarAssingNode(self, node: VarAssingNode, context: Context):
        var_name = node.var_name_token.value

        if not context.symbol_table.exists(var_name):
            raise TypeErrorDsl(f'{var_name} is not defined', node.position)

        value = self.visit(node.value_node, context) if not isinstance(node.value_node, Value) else node.value_node
        context.symbol_table.set(var_name, value)

        return Null()

    def visit_VarDefNode(self, node: VarDefNode, context: Context):
        var_name = node.var_name_token.value
        if node.value_node:
            value = self.visit(node.value_node, context) if not isinstance(node.value_node, Callable) else node.value_node
        else:
            value = Null()

        context.symbol_table.define(var_name, value, node.access)

        return Null()

    def visit_ListNode(self, node: ListNode, context: Context):
        elements = []

        for element_node in node.element_nodes:
            elements.append(self.visit(element_node, context))
        
        return List(elements)

    def visit_StatmentNode(self, node: StatmentNode, context: Context):
        return_value = None

        for element_node in node.element_nodes:
            value = self.visit(element_node, context)
            if isinstance(element_node, ReturnNode):
                return_value = value

        return return_value if return_value else Null()

    def visit_ImportNode(self, node: ImportNode, context: Context):
        value = node.value
        self.import_file(value, context)
        return Null()

    def visit_ReturnNode(self, node: ReturnNode, context: Context):
        return self.visit(node.value_node, context)

    def visit_ListAccessNode(self, node: ListAccessNode, context: Context):
        list_var: List = self.visit(node.list_node, context)
        index = self.visit(node.index_node, context)
        if index.value > list_var.get_lenght():
            raise IndexErrorDsl(f'index out of range', node.position)

        return list_var.get_element(index.value)

    def visit_ListAssingNode(self, node: ListAssingNode, context: Context):
        list_var = self.visit(node.list_node, context)
        index = self.visit(node.index_node, context)
        if index.value > list_var.getLenght():
            raise IndexErrorDsl(f'index out of range', node.position)

        value = self.visit(node.value_node, context)
        
        list_var.setElement(index.value, value)
        return Null()

    def visit_IfNode(self, node: IfNode, context: Context):
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

    def visit_ForNode(self, node: ForNode, context: Context):
        steps = node.steps
        identifier = node.identifier
        body_node = node.body_node

        context.symbol_table.define(identifier.value, Integer(0))
        for i in range(self.visit(steps, context).value):
            context.symbol_table.set(identifier.value, Integer(i))
            self.visit(body_node, context)
        context.symbol_table.remove(identifier.value)

        return Null()

    def visit_FuncDefNode(self, node: FuncDefNode, context: Context):
        func_name = node.func_name_token.value if node.func_name_token else None
        body_node = node.body_node

        arg_names = [name_token.value for name_token in node.arg_name_tokens]
        arg_types = [value_token.value if value_token else None for value_token in node.arg_type_tokens]

        args = []
        for i in range(len(arg_names)):
            args.append((arg_names[i], arg_types[i]))

        function = Function(func_name, body_node, args, context)

        if node.func_name_token:
            return self.visit(VarDefNode(node.position, node.func_name_token, value_node=function, access=node.access), context)
        else:
            return function

    def visit_TriggerDefNode(self, node: TriggerDefNode, context: Context):
        trigger_list = context.get_root_context().symbol_table.parent.symbols.get('@triggers')

        event = self.visit(node.event, context)

        args = []
        if event == EventType.MESSAGE:
            args = [('message', None)]
        elif event == EventType.LOGIN:
            pass
        elif event == EventType.SCHEDULE:
            pass
        else:
            pass

        function = Function('@trigger_function', node.body_node, args)

        trigger = Trigger(event, function, context)
        trigger_list.value.append_element(trigger)

        return Null()

    def visit_ClassDefNode(self, node: ClassDefNode, context: Context):
        class_name = node.class_name_token.value if node.class_name_token else None
        body_node = node.body_node

        new_class = Class(class_name, body_node)

        if node.class_name_token:
            return self.visit(VarDefNode(node.position, node.class_name_token, value_node=new_class, access=node.access), context)
        else:
            return new_class

    def visit_CallNode(self, node: CallNode, context: Context):
        args = []

        function = self.visit(node.func_node, context)
        if not isinstance(function, Callable):
            raise TypeErrorDsl((f'{node.func_node} is not callable'), node.position)
        
        for arg_node in node.arg_nodes:
            args.append(self.visit(arg_node, context))
            
        result = function.execute(args, context, self.visit)
        return result

    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context):
        if node.op_token.type == TokenType.MINUS:
            value = self.visit(node.node, context).value
            result = -value
            return Value(result).wrap()
        if node.op_token.type.matches(TokenType.KEYWORD, 'not'):
            value = self.visit(node.node, context)
            result = not value
            return Boolean(result)

    def visit_BinOpNode(self, node: BinOpNode, context: Context):
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
            elif op_token.type == TokenType.MOD:
                result = left.value % right.value

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
            raise TypeErrorDsl(f"Runtime math error: {left.type()}:{left.value} {op_token} {right.type()}:{right.value} {e}", node.position)


    def run(self, command, context):
        try:
            lexer = Lexer(command)
            tokens = lexer.generate_tokens()

            parser = Parser(tokens)
            ast = parser.parse()
            
            result = self.visit(ast, context)
            return 0
        except Error as e:
            return self.handle_error(e, command)

    # Execute dsl Function object
    # Args are python types
    # Wrapped args are dsl types
    def call(self, function, context, wrapped_args = [], args = []):
        try:
            if not isinstance(function, Callable):
                raise TypeErrorDsl((f'{function} is not callable'))

            for arg in args:
                value = Value(arg)
                wrapped_args.append(value.wrap())

            return function.execute(wrapped_args, context, self.visit)
        except Error as e:
            self.handle_error(e)


    def handle_error(self, error:Error, command = None):
        if error.position:
            start, end = error.position
            error_message = f'{error} at line {start.line} {f", character {start.character}" if not end else ""}\n{self.pointer_string(command, error.position)}'
        else:
            error_message = f'{error}'
        return error_message

    # DEBUG FUNCTIONS
    #######################################
    # Returns the string of tokens
    def tokenize(self, command, context):
        try:
            lexer = Lexer(command)
            tokens = lexer.generate_tokens()
            return list(tokens)
        except Error as e:
            if e.position:
                start, end = e.position
                error_message = f'{e} at line {start.line} {f", character {start.character}" if not end else ""}\n{self.pointer_string(command, e.position)}'
            else:
                error_message = f'{e}'
            return error_message

    # Returns the abstract syntax tree
    def parse(self, command, context):
        try:
            lexer = Lexer(command)
            tokens = lexer.fast_generate_tokens()

            parser = Parser(tokens)
            ast = parser.parse()
            return ast
        except Error as error:
            if error.position:
                start, end = error.position
                error_message = f'{error} at line {start.line} {f", character {start.character}" if not end else ""}\n{self.pointer_string(command, error.position)}'
            else:
                error_message = f'{error}'
            return error_message
    #########################################


    # TEMP CODE     TODO: Centralice the io access on either shell or interpreter
    def import_file(self, path, context):
        from os.path import exists
        if exists(f'built_in_modules/{path}.dsl'):          # Check if an equally named module exist in the built in modules
            path = f'built_in_modules/{path}.dsl'               # If it does, load that module instead
        elif exists(f'{path}.dsl'):                         # Check if the module exist
            path = f'{path}.dsl'
        else:
            raise TypeErrorDsl(f"No script named {file.name} found")

        lines = []
        with open(path, 'r') as file:
            lines += file.readlines()
            program = ''
            for line in lines:
                if '#' in line:
                    line = line[0:line.index('#')]
                program += line
            result = self.run(program, context)
            if result != 0:
                print(result)
            return result


    # Returns the given text with a pointer towards the character in the given position
    # May not work with long or multiline statmets
    def pointer_string(self, text, position):
        start, end = position
        lines = text.split('\n')

        if start.line > len(text):                  # TODO: change this crappy fix
            result = ''
            for i in range(len(lines)):
                result += f'{i}  {lines[i]}\n'
            return result


        whitespace  = [' ']
        pointer     = None
        end_pointer = None

        fix = len(str(start.line)) + 2                          # Fix 0 based numbering and line count hint
        pointer = whitespace * (start.character + fix) + ['^']

        if end:
            if start.line == end.line:
                pointer += ['^'] * (end.character - start.character)
            else:
                pointer += ['^'] * (len(lines[start.line]) - start.character)
                end_pointer = (whitespace * fix) + (['^'] * end.character)

        pointer = ''.join(pointer)
        lines[start.line] += f'\n{pointer}'

        if end_pointer:
            end_pointer = ''.join(end_pointer)
            lines[end.line] += f'\n{end_pointer}'

        result = ''
        for i in range(len(lines)):
            result += f'{i}  {lines[i]}\n'
        return result