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

    def execute(self, args, context: Context):
        
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

@dataclass(repr=False)
class Class(Callable):
    body_node: any

    def execute(self, args, context: Context):
        
        instance_context = Context(self.name, context.symbol_table, context)     # Copy parent context
        instance_context.symbol_table.remove(self.name)

        interpreter = Interpreter()                                                 
        interpreter.visit(self.body_node, context)                                  # execute body_node     # should contain function definitions and parameters ?

        constructor = instance_context.symbol_table.get(self.name)               # from the class body pick the function with the same name      # this definition overrides class symbol name inside the class
        if constructor:                                                             # check if has a user-defined constructor
            if not isinstance(constructor, Function):                               # check if the constructor is a function
                raise Exception((f'{constructor} is not callable'))
            arg_names = constructor.arg_names                                           # get the required arguments for the constructor
            self.check_args(args, arg_names)                                            # check if the class call arguments match
            constructor_context = self.create_context(args, arg_names, context)            # create the context of the future object
            result = constructor.execute(args, constructor_context)                        # constructor shares context with the instance of the future object     # result of the constructor can be ignored
        return Object(self.name, instance_context)
        

    def __repr__(self):
        return f'<class {self.name}>'

@dataclass(repr=False)
class Object:
    class_name: str
    object_context: Context

    def __init__(self, class_name: str, object_context: Context):
        self.class_name = class_name
        self.object_context = object_context
        self.object_context.symbol_table.set('this', self)

    def getAttribute(self, attr):
        return self.object_context.symbol_table.get(attr)

    def setAttribute(self, attr, value):
        self.object_context.symbol_table.set(attr, value)

    def __repr__(self):
        return f'<{self.class_name} object>'