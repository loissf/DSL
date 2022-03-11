from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):

    INT             = 0     # integer numbers
    FLOAT           = 1     # floating point numbers
    IDENTIFIER      = 2     # char((char|number|'_')*)?
    KEYWORD         = 3     # var, if, function...
    EQUALS          = 4     # =
    PLUS            = 5     # +
    MINUS           = 6     # -
    MULTIPLY        = 7     # *
    DIVIDE          = 8     # /
    MOD             = 9     # %
    LPAREN          = 10     # (
    RPAREN          = 11    # )
    LSQUARE         = 12    # [
    RSQUARE         = 13    # [
    DOUBLE_EQUALS   = 14    # ==
    NOT_EQUALS      = 15    # !=
    GREATER         = 16    # >
    LOWER           = 17    # <
    GREATER_EQUALS  = 18    # >=
    LOWER_EQUALS    = 19    # <=
    STRING          = 20    # " "
    COLON           = 21    # :
    COMMA           = 22    # ,
    DOT             = 23    # .
    EOL             = 24    # end of line
    EOF             = 25    # end of file

# Groups of token types that are parsed together in the same node
@dataclass
class TypeGroups:

    ARITHMETIC_OP = [
        TokenType.PLUS,             TokenType.MINUS,
        TokenType.MULTIPLY,         TokenType.DIVIDE,
        TokenType.MOD
    ]

    COMPARATION_OP = [
        TokenType.DOUBLE_EQUALS,    TokenType.NOT_EQUALS,
        TokenType.GREATER,          TokenType.GREATER_EQUALS,
        TokenType.LOWER,            TokenType.LOWER_EQUALS
    ]

@dataclass
class Position:
    character: int
    line:      int

    def copy(self):
        return Position(self.character, self.line)

# Holds the type and value of a token 
# Holds the position in the program string for display in case of an error
@dataclass
class Token:
    type: TokenType
    position: tuple[Position, Position]
    value: any = None

    def matches(self, type, value):
        return self.type == type and self.value == value

    def __repr__(self):
        return self.type.name + (f":{self.value}" if self.value != None else "")