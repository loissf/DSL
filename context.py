from dataclasses import dataclass
from enum import Enum

class AccessType(Enum):
    PRIVATE = 0
    PUBLIC  = 1

@dataclass
class Variable:
    value: any
    access: AccessType

    def __repr__(self):
        return (f'{self.access}' if self.access == AccessType.PRIVATE else '') + f'{self.value}'

# Holds a dictionary of symbol names and values
# Holds a parent symbol table if any that checks in no key matches
class SymbolTable:

    def __init__(self, parent = None):
        self.symbols = {}
        self.parent = parent

    # Returns the value with matching key, if local=True, doesnt check parent symbol tables
    def get(self, name):
        variable = self.symbols.get(name)
        if variable == None:
            if self.parent:
                value = self.parent.get(name)
            else:
                value = None
        else:
            value = variable.value
        return value

    def get_local(self, name):
        variable = self.symbols.get(name)
        return variable.value if variable else None

    def get_access(self, name):
        variable = self.symbols.get(name)
        return variable.access if variable else None

    # Sets a value in the table, this locally overrides parent symbols with the same key
    def set(self, name, value):
        variable = self.symbols.get(name)
        if variable:
            variable.value = value

    def define(self, name, value, access=AccessType.PUBLIC):
        self.symbols[name] = Variable(value, access)

    def remove(self, name):
        if name in self.symbols:
            del self.symbols[name]
    
    def exists(self, name):
        return name in self.symbols
        
    def __repr__(self):
        table = ''
        for symbol in self.symbols:
            variable = self.symbols[symbol]
            table += f'{str.lower(variable.access.name)}:' if variable.access != AccessType.PUBLIC else ''
            table += f'{symbol}'
            table += f'<-{variable.value}'
        return f'{table}'

# Holds a context name, symbol table and parent if any
@dataclass
class Context:
    display_name: str
    symbol_table: SymbolTable
    parent: any = None
    output: any = None

    def __init__(self, display_name: str, symbol_table: SymbolTable, parent = None, output = None):
        self.display_name = display_name
        self.symbol_table = symbol_table
        self.parent = parent
        self.output = output

    # Sends an asyncronous callback with the output value
    def send_output(self, value):
        if self.output:
            import asyncio
            loop = asyncio._get_running_loop()
            if loop:
                asyncio.get_event_loop().create_task(self.output(value))
            else:
                asyncio.run(self.output(value))
        elif self.parent:
            self.parent.send_output(value)

    # Returns the root context of the context hierarchy
    def get_root_context(self):
        if self.parent:
            return self.parent.get_root_context()
        else:
            return self

    # Returns the context hierarchy
    def get_hierarchy(self):
        context = ''
        if self.parent:
            context += f'{self}\n{self.parent.get_hierarchy()}'
        else:
            context += f'{self}\n'
        return context

    def copy(self):
        return Context(self.display_name, self.symbol_table, self.parent, self.output)

    def __repr__(self):
        return f'<{self.display_name}>'