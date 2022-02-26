from dataclasses import dataclass
from tokens import Token, TokenType

# DEFINITION OF THE ABSTRACT SYNTAX TREE NODES
# The abstract syntax tree is a node itself, that may have more nodes as parameters
# The root node is the entry point for the interpreter

@dataclass
class Node:
    position: int

@dataclass
class ValueNode(Node):
    token: Token
    value: any

    def __init__(self, token: Token, value: any):
        super().__init__(token.position)
        self.token = token
        self.value = value
    
    def __repr__(self):
        return f'{self.token.value}'

@dataclass(repr=False, init=False)
class NumberNode(ValueNode):
    value: float

@dataclass(repr=False, init=False)
class StringNode(ValueNode):
    value: str

@dataclass(repr=False, init=False)
class BooleanNode(ValueNode):
    value: bool

@dataclass(repr=False, init=False)
class VoidNode(ValueNode):

    def __init__(self, token):
        super().__init__(token, None)

@dataclass
class ParentContextNode(Node):
    token: Token

@dataclass
class ListNode(Node):
    element_nodes: []

    def __repr__(self):
        return f'LIST{self.element_nodes}'

@dataclass
class VarAccessNode(Node):
    var_name_token: Token

    def __init__(self, var_name_token: Token):
        super().__init__(var_name_token.position)
        self.var_name_token = var_name_token

    def __repr__(self):
        return f'{self.var_name_token}'

@dataclass
class VarAssingNode(Node):
    var_name_token: Token
    value_node: Node

    def __repr__(self):
        return f'{self.var_name_token}<-{self.value_node}'

@dataclass
class AttributeAccessNode(Node):
    value_node: VarAccessNode
    attribute_node: VarAccessNode

@dataclass(repr=False)
class ListAccessNode(Node):
    list_node: VarAccessNode
    index_node: NumberNode

    def __init__(self, list_node: VarAccessNode, index_node: NumberNode):
        super().__init__(list_node.position)
        self.list_node = list_node
        self.index_node = index_node

    def __repr__(self):
        return f'{self.list_node}'

@dataclass(repr=False)
class ListAssingNode(Node):
    list_node: VarAccessNode
    index_node: NumberNode
    value_node: Node

    def __init__(self, list_node: VarAccessNode, index_node: NumberNode, value_node: Node):
        super().__init__(list_node.position)
        self.list_node = list_node
        self.index_node = index_node
        self.value_node = value_node

    def __repr__(self):
        return f'{self.var_name_token}<-{self.value_node}'

@dataclass
class BinOpNode(Node):
    left_node: Node
    op_token: Token
    right_node: Node

    def __init__(self, left_node: Node, op_token: Token, right_node: Node):
        super().__init__(left_node.position)
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

@dataclass
class UnaryOpNode(Node):
    op_token: Token
    node: Node

    def __init__(self, op_token: Token, node: Node):
        super().__init__(op_token.position)
        self.op_token = op_token
        self.node = node

    def __repr__(self):
        return f'({self.op_token}, {self.node})'
# NOW A BUILT IN FUNCTION
'''
@dataclass
class WriteNode(Node):
    value_node: StringNode

    def __repr__(self):
        return f'PRINT "{self.value_node}"'
'''
@dataclass
class IfNode(Node):
    condition: any
    if_case: any
    else_case: any = None

    def __repr__(self):
        return f'If {self.condition}: {self.if_case}' if self.else_case == None else f'If {self.condition}: {self.if_case} else: {self.else_case}'

@dataclass
class FuncDefNode(Node):
    body_node: Node
    func_name_token: Token = None
    arg_name_tokens: [] = None

    def __repr__(self):
        func_name = f'{self.func_name_token.value}' if self.func_name_token != None else '<anonymus>'
        return f'{func_name}<-FUNCTION(args({self.arg_name_tokens}) body({self.body_node}))'

@dataclass
class ClassDefNode(Node):
    body_node: Node
    class_name_token: Token = None

    def __repr__(self):
        class_name = f'{self.class_name_token.value}' if self.class_name_token != None else '<anonymus>'
        return f'{class_name}<-CLASS body({self.body_node}))'

@dataclass
class CallNode(Node):
    func_node: VarAccessNode
    arg_nodes: []

    def __init__(self, func_node: VarAccessNode, arg_nodes: []):
        super().__init__(func_node.position)
        self.func_node = func_node
        self.arg_nodes = arg_nodes

    def __repr__(self):
        return f'CALL->{self.func_node}(args({self.arg_nodes}))'