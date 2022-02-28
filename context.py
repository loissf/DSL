from dataclasses import dataclass

class SymbolTable:

    def __init__(self, parent = None):
        self.symbols = {}
        self.parent = parent

    def get(self, name, local: bool = False):
        value = self.symbols.get(name, None)

        if not local:
            if value == None and self.parent:
                value = self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]
        
    def __repr__(self):
        table = ''
        for symbol in self.symbols:
            table += f'{symbol} : {self.symbols.get(symbol)}\n'
        return f'{table}'

@dataclass
class Context:
    display_name: str
    symbol_table: SymbolTable
    parent: any = None
    output: str = None

    def send_output(self, text):
        root_context = self.get_root_context()
        if root_context.output:
            root_context.output += text
        else:
            root_context.output = text

    def get_output(self):
        if self.output:
            return_value = self.output
            self.output = None
            return return_value

    def get_root_context(self):
        if self.parent:
            return self.parent.get_root_context()
        else:
            return self

    def __repr__(self):
        return f'<{self.display_name}>'