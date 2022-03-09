import lexer
import parser_
import interpreter
import context

from lexer          import Lexer
from parser_        import Parser
from interpreter    import Interpreter
from context        import *

from errors         import Error
from values         import BuiltInFunction, List, Callable, Value, Object

# BUILT IN FUNCTIONS
built_ins = SymbolTable()

built_ins.set('write', BuiltInFunction.write)
built_ins.set('context', BuiltInFunction.context)
built_ins.set('symbols', BuiltInFunction.symbols)
built_ins.set('triggers', BuiltInFunction.triggers)
built_ins.set('substring', BuiltInFunction.substring)
built_ins.set('contains', BuiltInFunction.contains)
built_ins.set('string', BuiltInFunction.string)
built_ins.set('length', BuiltInFunction.length)
built_ins.set('time', BuiltInFunction.time)
built_ins.set('dump', BuiltInFunction.dump)

# BUILT IN FUNCTIONS


# GLOBAL VARIABLES  

built_ins.set('@triggers', List([]))    # @triggers cant be accessed by users, due to @ raising IllegalCharError
built_ins.set('on_message', 0)

built_ins.set('@guilds', List([]))
built_ins.set('@direct_messages', List([]))

# GLOBAL VARIABLES


class Shell:

    def __init__(self, output_callback, guild=None, channel=None):
        
        # BUILT INS INITIALIZATION
        self.context = Context('built_ins', built_ins)
        self.open_file('core.dsl')

        # ROOT CONTEXT
        symbol_table = SymbolTable(built_ins)
        self.shell = Context('shell', symbol_table)

        # CALLBACK
        self.output_callback = output_callback

        # SET CONTEXT
        self.change_context(output_callback, guild, channel)

    
    # Executes a command and returns either the console output or an error message
    def run_command(self, command):
        interpreter = Interpreter()

        try:
            return interpreter.run(command, self.context)
        except Exception as e:
            import traceback
            traceback.print_exc()


    # Checks the trigger list with the current message and executes the matching ones
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
                
                self.execute_call(element.function, args, element.trigger_context, wrapped_args)
                # print(element.function.body_node) # check trigger structure

            except Error as e:
                error_message = f'```{e} in line {e.position.line}, character {e.position.character}\n{self.pointer_string(text, e.position)}```'
                return error_message
            except Exception as e:
                error_message = f'Exception: {e}'
                return error_message


    # Opens file, if its extension matches .dsl, executes its contents
    # otherwise reads it as text aka console input
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

    # Calls a callable type checking is type and wrapping its arguments into dsl values
    # Can receive already wrapped args optionally
    def execute_call(self, function, args, context, wrapped_args = None):
        if not isinstance(function, Callable):
            raise Error((f'{function} is not callable'))

        if not wrapped_args:
            wrapped_args = []
        for arg in args:
            value = Value(arg)
            wrapped_args.append(value.wrap())
        return function.execute(wrapped_args, context)
    
    # CONTEXT
    #######################################
    def change_context(self, output_callback, guild = None, channel = None):
        self.context.output = None
        if guild:
            guild_list = self.shell.symbol_table.get('@guilds').value
            guild_context = None
            for element in guild_list:
                if element.display_name == guild:
                    guild_context = element
                    # break
            if not guild_context:
                guild_context = Context(guild, SymbolTable(self.shell.symbol_table), self.shell)
                guild_context.symbol_table.set('@channels', List([]))
                guild_list.append(guild_context)
        
            if channel:
                channel_list = guild_context.symbol_table.get('@channels').value
                channel_context = None
                for element in channel_list:
                    if element.display_name == channel:
                        channel_context = element
                        # break
                if not channel_context:
                    channel_context = Context(channel, SymbolTable(guild_context.symbol_table), guild_context)
                    channel_list.append(channel_context)
                self.context = channel_context
            else:
                self.context = guild_context

        elif channel:
            channel_list = self.shell.symbol_table.get('@direct_messages').value
            channel_context = None
            for element in channel_list:
                if element.display_name == channel:
                    channel_context = element
                    # break
            if not channel_context:
                channel_context = Context(channel, SymbolTable(self.shell.symbol_table), self.shell)
                channel_list.append(channel_context)
            self.context = channel_context

        else:
            self.context = self.shell

        self.context.output = self.output_callback
    #######################################

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