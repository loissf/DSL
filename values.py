from dataclasses import dataclass
from interpreter import Interpreter
from context import Context, SymbolTable

@dataclass
class Value:
    value: any

    def __repr__(self):
        return f'{self.value}'

@dataclass(repr=False)
class Number(Value):
    value: float

@dataclass(repr=False)
class String(Value):
    value: str

@dataclass(repr=False)
class Boolean(Value):
    value: bool

@dataclass(repr=False)
class List(Value):
    value: []

    def getElement(self, index):
        return self.value[int(index)]
        
    def setElement(self, index, value):
        self.value[int(index)] = value
            
@dataclass
class Callable:
    name: str

    def check_args(self, args, arg_names):
        if len(args) > len(arg_names):
            raise Exception(f'Too many arguments, expected {len(arg_names)} but {len(args)} where given')
        if len(args) < len(arg_names):
            raise Exception(f'Too few arguments, expected {len(arg_names)} but {len(args)} where given')

    def create_context(self, args, arg_names, parent):
        new_symbol_table = SymbolTable(parent.symbol_table)

        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
  
            new_symbol_table.set(arg_name, arg_value)

        new_context = Context(self.name, new_symbol_table, parent)
        return new_context

    def execute(self, args, context: Context):
        pass

@dataclass(repr=False)
class Function(Callable):
    body_node: any
    arg_names: []

    def execute(self, args, context: Context):
        interpreter = Interpreter()

        self.check_args(args, self.arg_names)
        new_context = self.create_context(args, self.arg_names, context)

        result = interpreter.visit(self.body_node, new_context)
        return result

    def __repr__(self):
        return f'<function {self.name}>'

@dataclass(repr=False)
class BuiltInFunction(Callable):

    def execute(self, args, context):
        
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name)

        self.check_args(args, method.arg_names)
        new_context = self.create_context(args, method.arg_names, context)

        result = method(new_context)
        return result

    def execute_write(self, context):
        value = str(context.symbol_table.get('value'))
        value += '\n'
        context.send_output(value)
        # print(value)
    execute_write.arg_names = ['value']

    def __repr__(self):
        return f'<built_in_function {self.name}>'

BuiltInFunction.write       = BuiltInFunction('write')