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

@dataclass
class Output:
    value: str = None

    def send_output(self, value):
        if self.value:
            self.value += value
        else:
            self.value = value

    def read_output(self):
        if self.value:
            return_value = self.value
            self.value = None
            return return_value

# Holds a context name, symbol table and parent if any
@dataclass
class Context:
    display_name: str
    symbol_table: SymbolTable
    parent: any = None
    output: Output = None

    def send_output(self, value):
        print(f'{self.display_name}: {value}')
        if self.output:
            self.output.send_output(value)
        else:
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

    def __repr__(self):
        return f'<{self.display_name}>'