from dataclasses import dataclass
import time

from context import Context, SymbolTable, AccessType
from errors  import TypeErrorDsl
from events  import EventType

# Parent class for base types that just hold a value
@dataclass
class Value:
    value: any

    def __repr__(self):
        return f'{self.value}'

    # Method that returns the value wrapped in the proper vale type
    def wrap(self):
        return _wrappers[type(self.value)](self.value)

    def equals(self, value):
        return self.value == value.value if isinstance(value, Value) else False

    def type(self):
        return 'value'

@dataclass(repr=False)
class Integer(Value):
    value: float

    def type(self):
        return 'int'

@dataclass(repr=False)
class Float(Value):
    value: float

    def type(self):
        return 'float'

@dataclass(repr=False)
class String(Value):
    value: str

    def type(self):
        return 'str'

@dataclass(repr=False)
class Boolean(Value):
    value: bool

    def type(self):
        return 'bool'

# Null type value, holds None
@dataclass(repr=False)
class Null(Value):
    value: None
    def __init__(self, value = None):
        super().__init__(None)

    def type(self):
        return 'value'

    def __repr__(self):
        return 'null'

# Type of value that stores a list of elements
@dataclass(repr=False)
class List(Value):
    value: any # list

    def get_element(self, index):
        return self.value[int(index)]

    def set_element(self, index, value):
        self.value[int(index)] = value

    def append_element(self, value):
        self.value.append(value)

    def get_lenght(self):
        return len(self.value)

    def type(self):
        return 'list'

# Python types as keys for Dsl types, for efficient Value wrapping
_wrappers = {
    int     : Integer,
    float   : Float,
    str     : String,
    bool    : Boolean,
    list    : List,
    type(None): Null,
}

# Parent class for all types that can be called with identifier() syntax
@dataclass
class Callable:
    name: str

    # TODO: arg checking and function declaration allow for default argument values
    def check_args(self, args, arg_names):
        if len(args) > len(arg_names):
            raise TypeErrorDsl(f'{self.name}() too many arguments, expected {len(arg_names)} but {len(args)} where given: args({arg_names})', None)
        if len(args) < len(arg_names):
            raise TypeErrorDsl(f'{self.name}() too few arguments, expected {len(arg_names)} but {len(args)} where given: args({arg_names})', None)

        for i in range(len(args)):
            arg_name, arg_type = arg_names[i]

            if arg_type and arg_type != args[i].type():
                raise TypeErrorDsl(f'{self.name}() expected argument type {arg_type}, found {args[i].type()} in {arg_name}', None)

    def create_context(self, args, arg_names, parent):
        new_symbol_table = SymbolTable(parent.symbol_table)

        for i in range(len(args)):
            arg_name, arg_type = arg_names[i]
            arg_value = args[i]

            new_symbol_table.define(arg_name, arg_value)

        new_context = Context(self.name, new_symbol_table, parent)
        return new_context

    def execute(self, args, context: Context, visit):
        pass

# User defined function
@dataclass(repr=False)
class Function(Callable):
    body_node: any
    arg_names: list[tuple]
    context: Context = None

    def execute(self, args, context: Context, visit):

        call_context = context if self.context is None else self.context
        self.check_args(args, self.arg_names)
        new_context = self.create_context(args, self.arg_names, call_context)

        result = visit(self.body_node, new_context)
        return result

    def __repr__(self):
        return f'<function {self.name}>'

# Built in functions
@dataclass(repr=False)
class BuiltInFunction(Callable):

    def execute(self, args, context: Context, visit = None):

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
    execute_write.arg_names = [('value', None)]

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
    execute_substring.arg_names = [('string', String), ('start', Integer), ('end', Integer)]

    def execute_contains(self, context: Context):
        string    = context.symbol_table.get('string').value
        substring = context.symbol_table.get('substring').value
        return Boolean(substring in string)
    execute_contains.arg_names = [('string', String), ('substring', String)]

    def execute_string(self, context: Context):
        value = context.symbol_table.get('value').value
        return String(str(value))
    execute_string.arg_names = [('value', None)]

    def execute_length(self, context: Context):
        value = context.symbol_table.get('list').value
        return Integer(len(value))
    execute_length.arg_names = ['list']

    def execute_time(self, context: Context):
        return Float(time.time())
    execute_time.arg_names = []

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
BuiltInFunction.time        = BuiltInFunction('time')
BuiltInFunction.dump        = BuiltInFunction('dump')

# User defined class, calling a class returns an object, instance of the class
@dataclass(repr=False)
class Class(Callable):
    body_node: any

    def execute(self, args, context: Context, visit):

        new_symbol_table = SymbolTable(context.symbol_table)
        instance_context = Context(self.name, new_symbol_table, context)

        visit(self.body_node, instance_context)

        new_object = Object(self.name, instance_context)

        constructor = instance_context.symbol_table.get_local(self.name)
        if constructor:
            if not isinstance(constructor, Function):
                raise TypeErrorDsl(f'{constructor} is not a function, but {type(constructor)} instead')
            constructor.execute(args, instance_context, visit)

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

        self.object_context.symbol_table.define('this', self, access=AccessType.PRIVATE)

    def get(self, name: str, context: Context = None):
        table = self.object_context.symbol_table
        if self.object_context in context.get_hierarchy():
            return table.get_local(name)
        elif table.get_access(name) == AccessType.PUBLIC:
            return table.get_local(name)

    def set(self, name: str, value, context: Context = None):
        table = self.object_context.symbol_table
        if self.object_context in context.get_hierarchy():
            return table.set(name, value)
        elif table.get_access(name) == AccessType.PUBLIC:
            return table.set(name, value)

    def type(self):
        return f'{self.class_name}'

    def copy(self):
        return Object(self.class_name, self.object_context)

    def __repr__(self):
        return f'<{self.class_name} object>'

# Holds the event key and function of a trigger
@dataclass
class Trigger:
    event: EventType
    function: Function
    trigger_context: Context

    def __repr__(self):
        return f'ON_{self.event.name} : {self.function.body_node}'