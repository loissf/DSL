from nodes import *
from tokens import Token, TokenType, TypeGroups
from errors import SyntaxError

class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.advance()

    def advance(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None      

    def statment(self):

        position = self.current_token.position
        expressions = []
        expressions.append(self.expr())

        while self.current_token != None and not ( self.current_token.matches(TokenType.KEYWORD, 'end') or self.current_token.type == TokenType.EOF ):
            if self.current_token.type != TokenType.COMMA:
                raise SyntaxError("Invalid syntax, expected ',' or end", self.current_token.position)
            self.advance()
            expressions.append(self.expr())
        self.advance()

        return ListNode(position, expressions)

    def expr(self):
        if self.current_token.matches(TokenType.KEYWORD, 'void'):
            token = self.current_token
            self.advance()
            return VoidNode(token)

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
        # WRITE IS NOW A BUILT IN FUNCTION
        '''
        elif self.current_token.matches(TokenType.KEYWORD, 'write'):
            position = self.current_token.position
            self.advance()
            
            value = self.expr()
            return WriteNode(position, value)
        '''
        return self.logic_op()

    def logic_op(self):
        left_node = self.comp_op()

        while self.current_token != None and (self.current_token.matches(TokenType.KEYWORD, 'and') or self.current_token.matches(TokenType.KEYWORD, 'or')):
            op_token = self.current_token
            self.advance()
            right_node = self.comp_op()
            left_node = BinOpNode(left_node, op_token, right_node)

        return left_node

    def comp_op(self):
        left_node = self.arith_op()

        if self.current_token != None and self.current_token.matches(TokenType.KEYWORD, 'not'):
            op_token = self.current_token
            self.advance()
            return UnaryOpNode(op_token, self.comp_op())

        elif self.current_token != None and self.current_token.type in TypeGroups.COMPARATION_OP:

            op_token = self.current_token
            self.advance()
            right_node = self.arith_op()
            left_node = BinOpNode(left_node, op_token, right_node)

        return left_node

    def arith_op(self):
        left_node = self.term()

        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token
            self.advance()
            right_node = self.term()
            left_node = BinOpNode(left_node, op_token, right_node)

        return left_node

    def term(self):
        left_node = self.factor()

        while self.current_token != None and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op_token = self.current_token
            self.advance()
            right_node = self.factor()
            left_node = BinOpNode(left_node, op_token, right_node)

        return left_node

    def factor(self):

        if self.current_token.type == TokenType.MINUS:
            op_token = self.current_token
            self.advance()
            return UnaryOpNode(op_token, self.factor())

        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            result = self.expr()
            if self.current_token.type != TokenType.RPAREN:
                raise SyntaxError("Invalid syntax, expected ')'", self.current_token.position)
            
            self.advance()
            return result

        elif self.current_token.matches(TokenType.KEYWORD, 'function'):
            return self.func_def()

        elif self.current_token.matches(TokenType.KEYWORD, 'if'):
            return self.if_expr()

        elif self.current_token.type == TokenType.LSQUARE:
            return self.list_expr()

        return self.call()

    def call(self):
        value = self.list_element()

        if self.current_token != None and self.current_token.type == TokenType.LPAREN:
            func_node = value
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
        
        return value

    def list_element(self):
        value = self.value()

        if self.current_token != None and self.current_token.type == TokenType.LSQUARE:
            list_node = value
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
        
        return value

    def value(self):
        token = self.current_token

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return VarAccessNode(token)

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

        return FuncDefNode(position, func_name_token, body_node, arg_name_tokens)


    def if_expr(self):
        condition = None
        if_case = None
        else_case = None

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


    def parse(self):
        if self.current_token.type == TokenType.EOF:
            return VoidNode(self.current_token)

        result = self.statment()

        if self.current_token:
            raise SyntaxError("Invalid syntax", self.current_token.position)

        return result