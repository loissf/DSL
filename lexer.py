from tokens import Token, TokenType
import string
from errors import IllegalCharError, SyntaxError

WHITESPACE          = ' \n\t'
DIGITS              = '0123456789'
LOGIC_OP            = '=!><'
LETTERS             = string.ascii_letters
LETTERS_DIGITS      = LETTERS + DIGITS

KEYWORDS = [
    'var',
#   'write',    NOW A BUILT IN FUNCTION
    'and',
    'or',
    'not',
    'true',
    'false',
    'if',
    'else',
    'function',
    'end',
    'class',
    'this',
    'void'
]

class Lexer:
    def __init__(self, text):
        self.text = iter(text)
        self.position = -1
        self.advance()

    def advance(self):
        try:
            self.current_char = next(self.text)
            self.position += 1
        except StopIteration:
            self.current_char = None

    # Lexer entry point, returns a generator object with all the tokens found
    def generate_tokens(self):
        while self.current_char != None:

            if self.current_char in WHITESPACE:
                self.advance()

            elif self.current_char in DIGITS:
                yield self.generate_number()

            elif self.current_char in LETTERS:
                yield self.generate_identifier()

            elif self.current_char in LOGIC_OP:
                yield self.generate_logic_op()

            elif self.current_char == '"':
                yield self.generate_string()
                
            elif self.current_char == '+':
                self.advance()
                yield Token(TokenType.PLUS, self.position)

            elif self.current_char == '-':
                self.advance()
                yield Token(TokenType.MINUS, self.position)

            elif self.current_char == '*':
                self.advance()
                yield Token(TokenType.MULTIPLY, self.position)

            elif self.current_char == '/':
                self.advance()
                yield Token(TokenType.DIVIDE, self.position)

            elif self.current_char == '(':
                self.advance()
                yield Token(TokenType.LPAREN, self.position)

            elif self.current_char == ')':
                self.advance()
                yield Token(TokenType.RPAREN, self.position)

            elif self.current_char == '[':
                self.advance()
                yield Token(TokenType.LSQUARE, self.position)

            elif self.current_char == ']':
                self.advance()
                yield Token(TokenType.RSQUARE, self.position)

            elif self.current_char == ':':
                self.advance()
                yield Token(TokenType.COLON, self.position)

            elif self.current_char == ',':
                self.advance()
                yield Token(TokenType.COMMA, self.position)

            elif self.current_char == '.':
                self.advance()
                yield Token(TokenType.DOT, self.position)
                
            else:
                char = self.current_char
                self.advance()
                raise IllegalCharError(f"'{char}'", self.position)

        yield Token(TokenType.EOF, self.position)
        
    # Generates number token with all digits found as value
    def generate_number(self):
        decimal_point_count = 0
        number = self.current_char
        start_position = self.position
        self.advance()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                decimal_point_count += 1
                if decimal_point_count > 1:
                    break

            number += self.current_char
            self.advance()

        return Token(TokenType.NUMBER, start_position, float(number))

    # Generates either double char or single char logic operator, or equals token
    def generate_logic_op(self):
        first_op = self.current_char
        start_position = self.position
        self.advance()
        
        if self.current_char != '=':
            if first_op == '=':
                token = Token(TokenType.EQUALS, start_position)
            elif first_op == '>':
                token = Token(TokenType.GREATER, start_position)
            elif first_op == '<':
                token = Token(TokenType.LOWER, start_position)
            elif first_op == '!':
                raise SyntaxError('Invalid syntax', start_position)
        elif self.current_char == '=':
            if first_op == '=':
                token = Token(TokenType.DOUBLE_EQUALS, start_position)
            elif first_op == '>':
                token = Token(TokenType.GREATER_EQUALS, start_position)
            elif first_op == '<':
                token = Token(TokenType.LOWER_EQUALS, start_position)
            elif first_op == '!':
                token = Token(TokenType.NOT_EQUALS, start_position)

        self.advance()
        return token
    
    # Generates string token with all characters found between '"' as value
    def generate_string(self):
        string = ''
        start_position = self.position
        self.advance()

        while self.current_char != None and self.current_char != '"':
            string += self.current_char
            self.advance()
            if self.current_char == None:
                raise SyntaxError('Unclosed string literal', start_position)
        self.advance()

        return Token(TokenType.STRING, start_position, string)

    # Generates identifier all characters, digits and '_' found as value
    def generate_identifier(self):
        identifier = ''
        start_position = self.position

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            identifier += self.current_char
            self.advance()

        # If the identifier found matches with any of the keywords, the returned token type will be keyword instead
        token_type = TokenType.KEYWORD if identifier in KEYWORDS else TokenType.IDENTIFIER
        return Token(token_type, start_position, identifier)
