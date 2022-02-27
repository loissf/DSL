from lexer          import Lexer
from parser_        import Parser
from interpreter    import Interpreter
from tokens         import TokenType, Token
from context        import Context, SymbolTable
from errors         import Error
from values         import BuiltInFunction

class Shell:

    def __init__(self):
        # ROOT CONTEXT
        self.context = Context('<shell>', SymbolTable())

        # BUILT IN FUNCTIONS
        self.context.symbol_table.set('write', BuiltInFunction.write)
        self.context.symbol_table.set('context', BuiltInFunction.context)
        # BUILT IN FUNCTIONS
    
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
        #except Exception as e:
            #error_message = f'{e}'
            #return error_message


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
