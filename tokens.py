from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):

    NUMBER          = 0     # 123456789
    IDENTIFIER      = 1     # char((char|number|'_')*)?
    KEYWORD         = 2     # var, if, function...
    EQUALS          = 3     # =
    PLUS            = 4     # +
    MINUS           = 5     # -
    MULTIPLY        = 6     # *
    DIVIDE          = 7     # /
    LPAREN          = 8     # (
    RPAREN          = 9     # )
    LSQUARE         = 10    # [
    RSQUARE         = 11    # [
    DOUBLE_EQUALS   = 12    # ==
    NOT_EQUALS      = 13    # !=
    GREATER         = 14    # >
    LOWER           = 15    # <
    GREATER_EQUALS  = 16    # >=
    LOWER_EQUALS    = 17    # <=
    STRING          = 18    # " "
    COLON           = 19    # :
    COMMA           = 20    # ,
    EOF             = 21    # end of file

@dataclass
class TypeGroups:

    ARITHMETIC_OP = [
        TokenType.PLUS,             TokenType.MINUS,
        TokenType.MULTIPLY,         TokenType.DIVIDE
    ]

    COMPARATION_OP = [
        TokenType.DOUBLE_EQUALS,    TokenType.NOT_EQUALS,
        TokenType.GREATER,          TokenType.GREATER_EQUALS,
        TokenType.LOWER,            TokenType.LOWER_EQUALS
    ]

@dataclass
class Token:
    type: TokenType
    position: int
    value: any = None
    

    def matches(self, type, value):
        return self.type == type and self.value == value

    def __repr__(self):
        return self.type.name + (f":{self.value}" if self.value != None else "")