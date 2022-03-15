import lexer
import parser_
import interpreter
import context

from lexer          import Lexer, TokenType
from parser_        import Parser
from interpreter    import Interpreter
from context        import *
from events         import *

from errors         import Error
from values         import BuiltInFunction, List, Callable, Value, Trigger

# BUILT IN FUNCTIONS
built_ins = SymbolTable()

built_ins.define('write', BuiltInFunction.write)
built_ins.define('context', BuiltInFunction.context)
built_ins.define('symbols', BuiltInFunction.symbols)
built_ins.define('triggers', BuiltInFunction.triggers)
built_ins.define('substring', BuiltInFunction.substring)
built_ins.define('contains', BuiltInFunction.contains)
built_ins.define('string', BuiltInFunction.string)
built_ins.define('length', BuiltInFunction.length)
built_ins.define('time', BuiltInFunction.time)
built_ins.define('dump', BuiltInFunction.dump)

# BUILT IN FUNCTIONS


# GLOBAL VARIABLES  

built_ins.define('@triggers', List([]))    # @triggers cant be accessed by users, due to @ raising IllegalCharError
built_ins.define('on_message', EventType.MESSAGE)

built_ins.define('@guilds', List([]))
built_ins.define('@direct_messages', List([]))

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

        # define CONTEXT
        self.change_context(output_callback, guild, channel)

    
    # Executes a command and returns either the console output or an error message
    def run_command(self, command):
        try:
            return Interpreter().run(command, self.context)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return e
            
    def get_tokens(self, command, formatted=False):
        tokens = Interpreter().tokenize(command, self.context)
        return tokens if not formatted else ''.join([str(token)+' ' for token in tokens])

    def get_ast(self, command):
        return Interpreter().parse(command, self.context)

    def throw_event(self, event: Event):
        trigger_list = built_ins.get('@triggers').value
        interpreter = Interpreter()

        matching = []
        for trigger in trigger_list:
            if trigger.event == event.type:
                matching.append(trigger)

        if event.type == EventType.MESSAGE:
            content, author, context = event.value

            message_args = [content, author, context]
            message_class = self.context.symbol_table.get('Message') # TODO: load core inside built_ins
            message_object = interpreter.call(message_class, self.context, wrapped_args=[], args=message_args)

            for trigger in matching:
                interpreter.call(trigger.function, trigger.trigger_context, wrapped_args=[message_object], args=[])


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
                guild_context.symbol_table.define('@channels', List([]))
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