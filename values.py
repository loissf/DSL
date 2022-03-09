import context
import interpreter as inter

from context import *
from errors  import TypeError

from dataclasses import dataclass

# Parent class for base types that just hold a value
@dataclass
class Value:
    value: any

    def __repr__(self):
        return f'{self.value}'

    # Method that returns the value wrapped in the proper vale type     # TODO: list type
    def wrap(self):
        value_type = type(self.value)
        if value_type == int:
            return Integer(self.value)
        elif value_type == float:
            return Float(self.value)
        elif value_type == str:
            return String(self.value)
        elif value_type == bool:
            return Boolean(self.value)
        elif self.value == None:
            return Null() 

@dataclass(repr=False)
class Integer(Value):
    value: float

@dataclass(repr=False)
class Float(Value):
    value: float

@dataclass(repr=False)
class String(Value):
    value: str

@dataclass(repr=False)
class Boolean(Value):
    value: bool

# Null type value, holds None and doesnt require parameters to construct
@dataclass(repr=False)
class Null(Value):
    value: None
    def __init__(self):
        self.value = None

    def __repr__(self):
        return f'null'

# Type of value that stores a list of elements, impelements methods to get, set and append elements
@dataclass(repr=False)
class List(Value):
    value: any # list

    def getElement(self, index):
        return self.value[int(index)]
        
    def setElement(self, index, value):
        self.value[int(index)] = value

    def appendElement(self, value):
        self.value.append(value)

    def getLenght(self):
        return len(self.value)

# TODO: Maybe swap all the interpreter.visit() calls to the interpreter, and Callable.execute returns the new context (?)

# Parent class for all types that can be called with identifier() syntax
@dataclass
class Callable:
    name: str

    # TODO: arg checking and function declaration allow for default argument values
    def check_args(self, args, arg_names):
        if len(args) > len(arg_names):
            raise TypeError(f'{self.name}() too many arguments, expected {len(arg_names)} but {len(args)} where given: args({arg_names})', None)
        if len(args) < len(arg_names):
            raise TypeError(f'{self.name}() too few arguments, expected {len(arg_names)} but {len(args)} where given: args({arg_names})', None)

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

# User defined function
@dataclass(repr=False)
class Function(Callable):
    body_node: any
    arg_names: any # list
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

# Built in functions
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
        context.send_output(value)
        return Null()
    execute_write.arg_names = ['value']
        
    def execute_context(self, context: Context):
        context.send_output(f'{context.parent.get_hierarchy()}')
        return Null()
    execute_context.arg_names = []

    def execute_symbols(self, context: Context):
        context.send_output(f'{context.parent.symbol_table}')
        return Null()
    execute_symbols.arg_names = []

    def execute_triggers(self, context: Context):
        trigger_list = context.get_root_context().symbol_table.parent.get("@triggers")
        for trigger in trigger_list.value:
            context.send_output(f'{trigger}\n')
        return Null()
    execute_triggers.arg_names = []

    # TODO: substitute substring and contains builtin functions for propper keywords and operators
    def execute_substring(self, context: Context):
        string = context.symbol_table.get('string').value
        start  = context.symbol_table.get('start').value
        end    = context.symbol_table.get('end').value
        return String(string[int(start):int(end)])
    execute_substring.arg_names = ['string', 'start', 'end']

    def execute_contains(self, context: Context):
        string    = context.symbol_table.get('string').value
        substring = context.symbol_table.get('substring').value
        return Boolean(substring in string)
    execute_contains.arg_names = ['string', 'substring']

    def execute_string(self, context: Context):
        value = context.symbol_table.get('value').value
        return String(str(value))
    execute_string.arg_names = ['value']

    def execute_length(self, context: Context):
        list = context.symbol_table.get('list').value
        return Integer(len(list))
    execute_length.arg_names = ['list']

    # TODO: dump all on no arguments, dump certain variables if given as argument (?)
    def execute_dump(self, context: Context):
        context.parent.symbol_table.symbols = {}
        return Null()
    execute_dump.arg_names = []

    def __repr__(self):
        return f'<built_in_function {self.name}>'

BuiltInFunction.write       = BuiltInFunction('write')
BuiltInFunction.context     = BuiltInFunction('context')
BuiltInFunction.symbols     = BuiltInFunction('symbols')
BuiltInFunction.triggers    = BuiltInFunction('triggers')
BuiltInFunction.substring   = BuiltInFunction('substring')
BuiltInFunction.contains    = BuiltInFunction('contains')
BuiltInFunction.string      = BuiltInFunction('string')
BuiltInFunction.length      = BuiltInFunction('length')
BuiltInFunction.dump        = BuiltInFunction('dump')

# User defined class, calling a class returns an object instance of the class
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
        return new_object
        

    def __repr__(self):
        return f'<class {self.name}>'

# Intance of a class
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

# Holds the event key and function of a trigger
@dataclass
class Trigger:
    event: int
    function: Function
    trigger_context: Context

    def __repr__(self):
        event = ''
        if self.event == 0:
            event = 'on_message'
        return f'{event} : {self.function}'