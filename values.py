import context
import interpreter as inter

from context import *
# from interpreter import *

from dataclasses import dataclass


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
class Null(Value):
    value: None
    def __init__(self):
        self.value = None

    def __repr__(self):
        return f'null'

@dataclass(repr=False)
class List(Value):
    value: []

    def getElement(self, index):
        return self.value[int(index)]
        
    def setElement(self, index, value):
        self.value[int(index)] = value

    def appendElement(self, value):
        self.value.append(value)

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
    context: Context = None
    
    def execute(self, args, context: Context):
        interpreter = inter.Interpreter()

        call_context = context if self.context == None else self.context
        self.check_args(args, self.arg_names)
        new_context = self.create_context(args, self.arg_names, call_context)

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

    def execute_write(self, context: Context):
        value = str(context.symbol_table.get('value'))
        value += '\n'
        context.send_output(value)
        # print(value)
    execute_write.arg_names = ['value']
        
    def execute_context(self, context: Context):
        context.send_output(f'{context.parent}')
    execute_context.arg_names = []

    def execute_symbols(self, context: Context):
        context.send_output(f'{context.parent.symbol_table}')
    execute_symbols.arg_names = []

    def execute_triggers(self, context: Context):
        trigger_list = context.get_root_context().symbol_table.parent.get("@triggers").value
        for trigger in trigger_list:
            context.send_output(f'{trigger}')
    execute_triggers.arg_names = []

    def __repr__(self):
        return f'<built_in_function {self.name}>'

BuiltInFunction.write       = BuiltInFunction('write')
BuiltInFunction.context     = BuiltInFunction('context')
BuiltInFunction.symbols     = BuiltInFunction('symbols')
BuiltInFunction.triggers    = BuiltInFunction('triggers')

@dataclass(repr=False)
class Class(Callable):
    body_node: any

    def execute(self, args, context: Context):
        
        new_symbol_table = SymbolTable(context.symbol_table)
        instance_context = Context(self.name, new_symbol_table, context)

        interpreter = inter.Interpreter()                                                 
        interpreter.visit(self.body_node, instance_context)

        new_object = Object(self.name, instance_context)                                 

        constructor = instance_context.symbol_table.get(self.name, True)                
        if constructor:
            if not isinstance(constructor, Function):
                raise Exception(f'{constructor} is not a function')
            constructor.execute(args, instance_context)
        '''
        if constructor:                                                              # check if has a user-defined constructor
            if not isinstance(constructor, Function):                                   # check if the constructor is a function
                raise Exception((f'{constructor} is not callable'))
            arg_names = constructor.arg_names                                           # get the required arguments for the constructor
            self.check_args(args, arg_names)                                            # check if the class call arguments match
            constructor_context = self.create_context(args, arg_names, context)            # create the context of the future object
            result = constructor.execute(args, constructor_context)                        # constructor shares context with the instance of the future object     # result of the constructor can be ignored
        '''
        return new_object
        

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

@dataclass
class Trigger:
    event: int
    trigger: any
    function: Function

    def __repr__(self):
        event = ''
        if self.event == 0:
            event = 'on_message'
        return f'{event} : {self.trigger} : {self.function}'