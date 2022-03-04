from dataclasses import dataclass

# Holds a dictionary of symbol names and values
# Holds a parent symbol table if any that checks in no key matches
class SymbolTable:

    def __init__(self, parent = None):
        self.symbols = {}
        self.parent = parent

    # Returns the value with matching key, if local=True, doesnt check parent symbol tables
    def get(self, name, local: bool = False):
        value = self.symbols.get(name, None)

        if not local:
            if value == None and self.parent:
                value = self.parent.get(name)
        return value

    # Sets a value in the table, this locally overrides parent symbols with the same key
    def set(self, name, value):
        self.symbols[name] = value

    # Removes a value from the table
    def remove(self, name):
        del self.symbols[name]
        
    def __repr__(self):
        table = ''
        for symbol in self.symbols:
            table += f'{symbol} : {self.symbols.get(symbol)}\n'
        return f'{table}'

# Holds a context name, symbol table and parent if any
# In case of been the root context may hold some output
@dataclass
class Context:
    display_name: str
    symbol_table: SymbolTable
    parent: any = None
    output: str = None

    # Checks for the root context and sends the output to it
    def send_output(self, text):
        root_context = self.get_root_context()
        if root_context.output:
            root_context.output += text
        else:
            root_context.output = text

    # Returns and resets the output, one time read
    def get_output(self):
        if self.output:
            return_value = self.output
            self.output = None
            return return_value
    
    # Returns the root context of the context hierarchy
    def get_root_context(self):
        if self.parent:
            return self.parent.get_root_context()
        else:
            return self

    def __repr__(self):
        return f'<{self.display_name}>'