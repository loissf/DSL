import lexer
import parser_
import interpreter
import context

from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter
from context import *

from errors         import Error
from values         import BuiltInFunction, List

# BUILT IN FUNCTIONS
built_ins = SymbolTable()

built_ins.set('write', BuiltInFunction.write)
built_ins.set('context', BuiltInFunction.context)
built_ins.set('symbols', BuiltInFunction.symbols)
built_ins.set('triggers', BuiltInFunction.triggers)

# BUILT IN FUNCTIONS

built_ins.set('@triggers', List([]))
built_ins.set('on_message', 0)


class Shell:

    def __init__(self):
        # ROOT CONTEXT
        symbol_table = SymbolTable(built_ins)
        print(symbol_table)
        self.context = Context('shell', symbol_table)

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
            error_message = f'{e}\n{self.pointer_string(command, e.position)}'
            return error_message
        except Exception as e:
            error_message = f'{e}'
            return error_message

    def input_text(self, text):
        trigger_list = built_ins.get('@triggers').value
        for element in trigger_list:
            if element.event == 0:
                if element.trigger.value == text:
                    try:
                        element.function.execute([], self.context)
                        return self.context.get_output()
                    except Error as e:
                        error_message = f'{e}\n{self.pointer_string(command, e.position)}'
                        return error_message
                    except Exception as e:
                        error_message = f'{e}'
                        return error_message

    # DEBUG FUNCTIONS
    #######################################
    # Returns the string of tokens
    def tokenize_command(self, command):
        try:
            lexer = Lexer(command)
            tokens = lexer.generate_tokens()
            return list(tokens)
        except Error as e:
            error_message = f'{e}\n{self.pointer_string(command, e.position)}'
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
            error_message = f'{e}\n{self.pointer_string(command, e.position)}'
            return error_message
    #########################################

    # Returns the given text with a pointer towards the character in the given position
    # May not work with long or multiline statmets
    def pointer_string(self, text, position):
        whitespace = [' ']
        pointer = whitespace * (position-1) + ['^'] + whitespace * (len(text) - position)
        pointer = ''.join(pointer)
        return f'{text}\n{pointer}'
