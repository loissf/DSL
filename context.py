from dataclasses import dataclass

class SymbolTable:

    def __init__(self, parent = None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            value = self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

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

