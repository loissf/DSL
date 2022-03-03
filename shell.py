import lexer
import parser_
import interpreter
import context

from lexer          import Lexer
from parser_        import Parser
from interpreter    import Interpreter
from context        import *

from errors         import Error
from values         import BuiltInFunction, List, Callable, Value

# BUILT IN FUNCTIONS
built_ins = SymbolTable()

built_ins.set('write', BuiltInFunction.write)
built_ins.set('context', BuiltInFunction.context)
built_ins.set('symbols', BuiltInFunction.symbols)
built_ins.set('triggers', BuiltInFunction.triggers)
built_ins.set('substring', BuiltInFunction.substring)

# BUILT IN FUNCTIONS

built_ins.set('@triggers', List([]))
built_ins.set('on_message', 0)


class Shell:

    def __init__(self):
        # BUILT INS INITIALIZATION
        # built_ins_context = Context('built_ins', built_ins)
        # self.open_file('core.dsl')
        # ROOT CONTEXT
        symbol_table = SymbolTable(built_ins)
        self.context = Context('shell', symbol_table)
        self.open_file('core.dsl')

    # Executes a command and returns either the console output or an error message
    def run_command(self, command):
        try:
            lexer = Lexer(command)
            tokens = lexer.generate_tokens()

            parser = Parser(tokens)
            ast = parser.parse()

            interpreter = Interpreter()
            result = interpreter.visit(ast, self.context)
            return self.context.get_output()
        except Error as e:
            if e.position:
                error_message = f'{e} in line {e.position.line}, character {e.position.character}\n{self.pointer_string(command, e.position)}'
            else:
                error_message = f'{e}'
            return error_message
        except Exception as e:
            error_message = f'{e}'
            return error_message

    def input_text(self, text, author = None, context = None):
        trigger_list = built_ins.get('@triggers').value
        for element in trigger_list:
            args = []           # python type values
            wrapped_args = []   # dsl type values       # values wrapped inside dsl types
            try:

                if element.event == 0:
                    message_class = self.context.symbol_table.get('Message') # TODO: load core inside built_ins
                    message_object = self.execute_call(message_class,
                                                       [text, author, context],
                                                       self.context)
                    wrapped_args.append(message_object)
                
                self.execute_call(element.function, args, self.context, wrapped_args)
                # print(element.function.body_node) # check trigger structure

                return self.context.get_output()

            except Error as e:
                error_message = f'{e} in line {e.position.line}, character {e.position.character}\n{self.pointer_string(text, e.position)}'
                return error_message
            except Exception as e:
                error_message = f'Exception: {e}'
                return error_message

    def open_file(self, path):
        lines = []
        with open(path, 'r') as file:
            if file.name.split('.')[1] == 'dsl':
                lines += file.readlines()
                program = ''
                for line in lines:
                    if '#' in line:
                        line = line[0:line.index('#')]
                    program += line
                return self.run_command(program)
            else:
                text = file.read()
                return self.input_text(text)

    # DEBUG FUNCTIONS
    #######################################

    # Returns the string of tokens
    def tokenize_command(self, command):
        try:
            lexer = Lexer(command)
            tokens = lexer.generate_tokens()
            return list(tokens)
        except Error as e:
            error_message = f'{e} in line {e.position.line}, character {e.position.character}\n{self.pointer_string(command, e.position)}'
            return error_message
    
    # Returns the abstract syntax tree
    def parse_command(self, command):
        try:
            lexer = Lexer(command)
            tokens = lexer.generate_tokens()

            parser = Parser(tokens)
            ast = parser.parse()
            return ast
        except Error as e:
            error_message = f'{e} in line {e.position.line}, character {e.position.character}\n{self.pointer_string(command, e.position)}'
            return error_message

    #########################################

    def execute_call(self, function, args, context, wrapped_args = None):
        if not isinstance(function, Callable):
            raise Error((f'{function} is not callable'))

        if not wrapped_args:
            wrapped_args = []
        for arg in args:
            value = Value(arg)
            wrapped_args.append(value.wrap())
        return function.execute(wrapped_args, context)

    # Returns the given text with a pointer towards the character in the given position
    # May not work with long or multiline statmets
    def pointer_string(self, text, position):
        whitespace = [' ']
        pointer = whitespace * (position.character-1 + len(str(position.line))) + ['^']
        pointer = ''.join(pointer)

        lines = text.split('\n')
        lines[position.line] += f'\n{pointer}'

        result = ''
        for i in range(len(lines)):
            result += f'{i}  {lines[i]}\n'
        return result
