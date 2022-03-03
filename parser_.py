import nodes
import tokens

from nodes  import *
from tokens import *

from errors import SyntaxError

class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.advance()

    # Parsing rules can be found in grammar.txt

    # Stores the next token from the iterator in current_token
    # until no more tokens are available
    def advance(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None      

    def statment(self):
        
        while self.current_token.type == TokenType.EOL:
                self.advance()

        position = self.current_token.position
        expressions = []
        expressions.append(self.expr())

        while self.current_token != None and not ( self.current_token.matches(TokenType.KEYWORD, 'end') or self.current_token.type == TokenType.EOF ):
            
            if not ( self.current_token.type == TokenType.COMMA or self.current_token.type == TokenType.EOL ):
                raise SyntaxError("Invalid syntax, expected ',' or end", self.current_token.position)

            if self.current_token.type == TokenType.COMMA:
                self.advance()
            while self.current_token.type == TokenType.EOL:
                self.advance()
            if not self.current_token.matches(TokenType.KEYWORD, 'end'):
                expressions.append(self.expr())
            else:
                # self.advance()
                pass # Possible SyntaxError("Invalid syntax, statment")

        while self.current_token.type == TokenType.EOL:
            self.advance()
        if self.current_token.matches(TokenType.KEYWORD, 'end'):
            self.advance()
        elif not self.current_token.type == TokenType.EOF:
            raise SyntaxError("Invalid syntax, expected end", self.current_token.position)

        return ListNode(position, expressions)

    def expr(self):

        # VoidNode              void
        ######################################################
        if self.current_token.matches(TokenType.KEYWORD, 'void'):
            token = self.current_token
            self.advance()
            return VoidNode(token)
        #########

        # VarNode               var identifier = expression
        #############################
        if self.current_token.matches(TokenType.KEYWORD, 'var'):
            position = self.current_token.position
            
            self.advance()
             
            if self.current_token.type != TokenType.IDENTIFIER:
                raise SyntaxError("Invalid syntax, expected identifier", self.current_token.position)
            var_name = self.current_token
            self.advance()

            if self.current_token.type != TokenType.EQUALS:
                raise SyntaxError("Invalid syntax, expected '='", self.current_token.position)
            self.advance()

            value = self.expr()
            return VarAssingNode(position, var_name, value)
        #############################

        return self.logic_op()

    def logic_op(self):
        left_node = self.comp_op()

        # BinOpNode             comparation_operation token comparation
        # for 'and' , 'or' logic operators
        ##########
        while self.current_token != None and (self.current_token.matches(TokenType.KEYWORD, 'and') or self.current_token.matches(TokenType.KEYWORD, 'or')):
            op_token = self.current_token
            self.advance()
            right_node = self.comp_op()
            left_node = BinOpNode(left_node, op_token, right_node)
        #############################

        return left_node

    def comp_op(self):
        left_node = self.arith_op()

        # UnaryOpNode           token arithmetic_operation
        # for 'not' logic operator
        ######################################################
        if self.current_token != None and self.current_token.matches(TokenType.KEYWORD, 'not'):
            op_token = self.current_token
            self.advance()
            return UnaryOpNode(op_token, self.comp_op())
        #############################

        # BinOpNode             arithmetic_operation token arithmetic_operation
        # for '>' , '<' , '==' , '>=' , '<=' , '!=' comparation operators
        ######################################################
        elif self.current_token != None and self.current_token.type in TypeGroups.COMPARATION_OP:

            op_token = self.current_token

            self.advance()

            right_node = self.arith_op()
            left_node = BinOpNode(left_node, op_token, right_node)
        #############################

        return left_node

    def arith_op(self):
        left_node = self.term()

        # BinOpNode             term token term
        # for '+' , '-' arithmetic operators
        ######################################################
        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token
            self.advance()
            right_node = self.term()
            left_node = BinOpNode(left_node, op_token, right_node)
        #############################

        return left_node

    def term(self):
        left_node = self.factor()

        # BinOpNode             factor token factor
        # for '*' , '/' arithmetic operators
        ######################################################
        while self.current_token != None and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op_token = self.current_token
            self.advance()
            right_node = self.factor()
            left_node = BinOpNode(left_node, op_token, right_node)
        #############################

        return left_node

    def factor(self):
        
        # UnaryOpNode           token factor
        # for '-' arithmetic operator
        ######################################################
        if self.current_token.type == TokenType.MINUS:
            op_token = self.current_token
            self.advance()
            return UnaryOpNode(op_token, self.factor())
        #############################

        # Check for an entire new expression inside parentheses '( )'
        #                       left_paren expression right_paren
        ######################################################
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            result = self.expr()
            if self.current_token.type != TokenType.RPAREN:
                raise SyntaxError("Invalid syntax, expected ')'", self.current_token.position)
            
            self.advance()
            return result
        #############################

        # Compound statmets if , function definition , list definition , TODO for , while ...                 
        ######################################################
        elif self.current_token.matches(TokenType.KEYWORD, 'function'):
            return self.func_def()

        elif self.current_token.matches(TokenType.KEYWORD, 'trigger'):
            return self.trigger_def()

        elif self.current_token.matches(TokenType.KEYWORD, 'class'):
            return self.class_def() 

        elif self.current_token.matches(TokenType.KEYWORD, 'if'):
            return self.if_expr()

        elif self.current_token.type == TokenType.LSQUARE:
            return self.list_expr()
        #############################

        return self.list_element()

    def list_element(self):
        attribute = self.call()

        # ListAccessNode        call[]
        # ListAsssingNode       call[] = expression
        ######################################################
        if self.current_token != None and self.current_token.type == TokenType.LSQUARE:
            list_node = attribute
            index = None
            self.advance()

            if self.current_token.type == TokenType.RSQUARE:
                raise SyntaxError("Invalid syntax, expected value", self.current_token.position)
            else:
                index = self.expr()

                if self.current_token.type != TokenType.RSQUARE:
                    raise Exception(f"Invalid syntax, expected ']' found {self.current_token}")
            
                self.advance()

                if self.current_token != None and self.current_token.type == TokenType.EQUALS:
                    self.advance()
                    value_node = self.expr()
                    return ListAssingNode(list_node, index, value_node)
                else:
                    return ListAccessNode(list_node, index)
        #############################
        
        return attribute

    def call(self):
        attribute = self.attribute()

        # CallNode              attribute()
        ######################################################
        if self.current_token != None and self.current_token.type == TokenType.LPAREN:
            func_node = attribute
            arg_nodes = []
            self.advance()

            if self.current_token.type == TokenType.RPAREN:
                self.advance()
            else:
                arg_nodes.append(self.expr())

                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    arg_nodes.append(self.expr())

                if self.current_token.type != TokenType.RPAREN:
                    raise SyntaxError("Invalid syntax, expected ',' or ')'", self.current_token.position)
            
                self.advance()
            return CallNode(func_node, arg_nodes)
        #############################
        
        return attribute

    def attribute(self):
        value = self.value()
        position = self.current_token.position

        # AttributeAccessNode        identifier.attribute
        # AttributeAsssingNode       identifier.attribute = expression
        ######################################################
        if isinstance(value, VarAccessNode):
            object_value = value
            if self.current_token.type == TokenType.DOT:

                self.advance()
                attribute = self.call()

                if self.current_token != None and self.current_token.type == TokenType.EQUALS:
                    self.advance()
                    value_node = self.expr()
                    
                    return AttributeAssingNode(position, object_value, attribute, value_node)
                else:
                    return AttributeAccessNode(position, object_value, attribute)
        #############################

        return value

    def value(self):
        token = self.current_token

        # VarAccessNode             identifier
        ######################################################
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return VarAccessNode(token)

        elif token.matches(TokenType.KEYWORD, 'this'):
            self.advance()
            return VarAccessNode(token)
        #############################

        # ValueNodes
        ######################################################
        elif token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token, token.value)

        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(token, token.value)

        elif token.matches(TokenType.KEYWORD, 'true'):
            self.advance()
            return BooleanNode(token, True)

        elif token.matches(TokenType.KEYWORD, 'false'):
            self.advance()
            return BooleanNode(token, False)
        #############################

    # FunctionDefNode           function identifier(arguments): statment
    ######################################################################
    def func_def(self):    # TODO initialice function args on top
        position = self.current_token.position
        self.advance()

        if self.current_token.type == TokenType.IDENTIFIER:
            func_name_token = self.current_token
            self.advance()
            if self.current_token.type != TokenType.LPAREN:
                raise SyntaxError("Invalid syntax, expected '('", self.current_token.position)
        else:
            func_name_token = None
            if self.current_token.type != TokenType.LPAREN:
                raise SyntaxError("Invalid syntax, expected identifier or '('", self.current_token.position)

        self.advance()
        arg_name_tokens = []

        if self.current_token.type == TokenType.IDENTIFIER:
            arg_name_tokens.append(self.current_token)
            self.advance()

            while self.current_token.type == TokenType.COMMA:
                self.advance()

                if self.current_token.type != TokenType.IDENTIFIER:
                    raise SyntaxError("Invalid syntax, expected identifier", self.current_token.position)

                arg_name_tokens.append(self.current_token)
                self.advance()

            if self.current_token.type != TokenType.RPAREN:
                raise SyntaxError("Invalid syntax, expected ',' or ')'", self.current_token.position)
        
        else:
            if self.current_token.type != TokenType.RPAREN:
                raise SyntaxError("Invalid syntax, expected identifier or ')'", self.current_token.position)

        self.advance()

        if self.current_token.type != TokenType.COLON:
            raise SyntaxError("Invalid syntax, expected ':'", self.current_token.position)

        self.advance()

        body_node = self.statment()

        return FuncDefNode(position, body_node, func_name_token, arg_name_tokens)

    # TriggerDefNode           trigger event_identifier(arguments): statment
    # event_identifier are global constants with int values to identify the event type
    # trigger object is created and stored in @triggers = [] global variable
    # TODO: trigger event_identifier(logic_op): statment
    # TODO: equivalent to -> function trigger(message): if logic=op: statment()
    ######################################################################
    def trigger_def(self):
        event           = None
        args            = None
        body_node       = None

        position = self.current_token.position
        self.advance()

        if self.current_token.type == TokenType.IDENTIFIER:
            event = VarAccessNode(self.current_token)
            self.advance()
            if self.current_token.type != TokenType.LPAREN:
                raise SyntaxError("Invalid syntax, expected '('", self.current_token.position)
        else:
            raise SyntaxError("Invalid syntax, expected event type", self.current_token.position)

        self.advance()
        args = []

        if self.current_token.type == TokenType.STRING:
            args.append(self.current_token)
            self.advance()

            while self.current_token.type == TokenType.COMMA:
                self.advance()

                if self.current_token.type != TokenType.IDENTIFIER:
                    raise SyntaxError("Invalid syntax, expected identifier", self.current_token.position)

                args.append(self.current_token)
                self.advance()

            if self.current_token.type != TokenType.RPAREN:
                raise SyntaxError("Invalid syntax, expected ',' or ')'", self.current_token.position)
        
        else:
            if self.current_token.type != TokenType.RPAREN:
                raise SyntaxError("Invalid syntax, expected identifier or ')'", self.current_token.position)

        self.advance()

        if self.current_token.type != TokenType.COLON:
            raise SyntaxError("Invalid syntax, expected ':'", self.current_token.position)

        self.advance()

        body_node = self.statment()
        args = args[0] if len(args) == 1 else args

        return TriggerDefNode(position, body_node, event, args)

    # ClassDefNode           class identifier: statment
    # if statment contains function identifier, that function is called when creating the object as a constructor
    ######################################################################
    def class_def(self):
        position = self.current_token.position
        self.advance()

        if self.current_token.type == TokenType.IDENTIFIER:
            class_name_token = self.current_token
            self.advance()
            if self.current_token.type != TokenType.COLON:
                raise SyntaxError("Invalid syntax, expected ':'", self.current_token.position)
        else:
            class_name_token = None
            if self.current_token.type != TokenType.COLON:
                raise SyntaxError("Invalid syntax, expected identifier or ':'", self.current_token.position)

        self.advance()

        body_node = self.statment()
        return ClassDefNode(position, body_node, class_name_token)

    # IfNode                    if logic_operation: statment (else: statment)?
    ######################################################################
    def if_expr(self):
        condition   = None
        if_case     = None
        else_case   = None

        position = self.current_token.position
        
        self.advance()
        condition = self.logic_op()

        if self.current_token.type != TokenType.COLON:
            raise SyntaxError("Invalid syntax, expected ':'", self.current_token.position)

        self.advance()
        if_case = self.statment()

        if if_case == None:
            raise SyntaxError("Invalid syntax, expected expression", self.current_token.position)

        if self.current_token != None and self.current_token.matches(TokenType.KEYWORD, 'else'):
            self.advance()
            
            if self.current_token.type != TokenType.COLON:
                raise SyntaxError("Invalid syntax, expected ':'", self.current_token.position)

            self.advance()
            else_case = self.statment()

            return IfNode(position, condition, if_case, else_case)

        return IfNode(position, condition, if_case, None) 

    # ListNode                  [ expression (, expression)*? ]
    ######################################################################
    def list_expr(self):
        element_nodes = []
        
        position = self.current_token.position
        self.advance()

        if self.current_token.type == TokenType.RSQUARE:
            self.advance()
        else:
            element_nodes.append(self.expr())

            while self.current_token.type == TokenType.COMMA:
                self.advance()
                element_nodes.append(self.expr())

            if self.current_token.type != TokenType.RSQUARE:
                raise SyntaxError("Invalid syntax, expected ',' or ']'", self.current_token.position)
        
            self.advance()
        return ListNode(position, element_nodes)

    # Parser entry point, returns the root node of the abstract syntax tree
    # If the only token found is End Of File token return VoidNode aka None value
    ######################################################################
    def parse(self):
        if self.current_token.type == TokenType.EOF:
            return VoidNode(self.current_token)

        result = self.statment()

        if not self.current_token.type == TokenType.EOF:
            raise SyntaxError(f"Invalid syntax {result}", self.current_token.position)

        return result