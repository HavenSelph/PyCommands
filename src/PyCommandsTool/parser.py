from enum import Enum, auto
from typing import Any


class TokenTypes(Enum):
    # Keywords
    Identifier = auto()

    # Literals
    StringLiteral = auto()
    IntegerLiteral = auto()
    FloatingPointLiteral = auto()
    BooleanLiteral = auto()

    # Operators
    Equal = auto()
    Colon = auto()

    # Delimiters
    OpenParen = auto()
    CloseParen = auto()
    OpenBracket = auto()
    CloseBracket = auto()
    OpenBrace = auto()
    CloseBrace = auto()
    Comma = auto()

    # Misc
    Space = auto()


keywords = {
    "True": TokenTypes.BooleanLiteral,
    "False": TokenTypes.BooleanLiteral
}

characters = {
    "(": TokenTypes.OpenParen,
    ")": TokenTypes.CloseParen,
    "[": TokenTypes.OpenBracket,
    "]": TokenTypes.CloseBracket,
    "{": TokenTypes.OpenBrace,
    "}": TokenTypes.CloseBrace,
    ":": TokenTypes.Colon,
    ",": TokenTypes.Comma,
    "=": TokenTypes.Equal
}


class Token:
    def __init__(self, token_type: TokenTypes, value: str, pos) -> None:
        self.token_type = token_type
        self.value = value
        self.pos = pos

    def __repr__(self) -> str:
        return f"Token({self.token_type}, {self.value}, {self.pos})"


class Lexer:
    def __init__(self, text: str, clean_spaces: bool = True) -> None:
        self.text = text
        self.cursor = 0
        self.clean_spaces = clean_spaces
        if self.clean_spaces:
            self.text = self.text.strip()

    @property
    def at_cursor(self) -> str:
        return self.text[self.cursor]

    @property
    def eof(self) -> bool:
        return self.cursor >= len(self.text)

    def context_error(self, error_text: str, msg: str = None, before: int = 5, after: int = 5, cursor_override: int = 0) -> str:
        cursor = self.cursor+cursor_override
        before = min(before, cursor)
        after = min(after, len(self.text) - cursor - 1)
        context = self.text[cursor-before:cursor+after++1]
        message = f"{' '*before}{'^'} {msg}" if msg else ""
        return f"{error_text} at index {cursor}\n{context}\n{message}"

    def tokenize(self) -> list[Token]:
        out = []
        while not self.eof:
            match self.at_cursor:
                case char if char.isalpha():
                    tmp = ""
                    while not self.eof and self.at_cursor.isalnum():
                        tmp += self.at_cursor
                        self.cursor += 1
                    out.append(Token(keywords.get(tmp, TokenTypes.Identifier), tmp, self.cursor))
                case char if char.isnumeric():
                    tmp = ""
                    while not self.eof and (self.at_cursor.isnumeric() or self.at_cursor == "."):
                        if self.at_cursor == ".":
                            if "." in tmp:
                                raise ValueError(self.context_error("Invalid floating point literal", "A floating point literal cannot contain more than one decimal point"))
                        tmp += self.at_cursor
                        self.cursor += 1
                    if "." in tmp:
                        out.append(Token(TokenTypes.FloatingPointLiteral, tmp, self.cursor))
                    else:
                        out.append(Token(TokenTypes.IntegerLiteral, tmp, self.cursor))
                case char if char == "'" or char == '"':
                    tmp = ""
                    self.cursor += 1
                    while not self.eof and (self.at_cursor != char or self.text[self.cursor - 1] == "\\"):
                        tmp += self.at_cursor
                        self.cursor += 1
                    if self.eof:
                        raise SyntaxError(self.context_error("Unterminated string literal", "Expected closing quotation mark, but reached end of text.", cursor_override=-1-len(tmp), after=40))
                    out.append(Token(TokenTypes.StringLiteral, tmp, self.cursor))
                    self.cursor += 1
                case char if char.isspace():
                    out.append(Token(TokenTypes.Space, char, self.cursor))
                    self.cursor += 1
                case char:
                    if char not in characters:
                        raise SyntaxError(self.context_error("Unknown character", f"Unknown character: '{char}'"))
                    out.append(Token(characters[char], char, self.cursor))
                    self.cursor += 1
        if self.clean_spaces:
            out = [token for i, token in enumerate(out) if ((token.token_type != out[i - 1].token_type or token.token_type != TokenTypes.Space) or i == 0)]
        return out


class Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.tokens = Lexer(text).tokenize()
        self.cursor = 0
        self.kwargs = False

    @property
    def at_cursor(self) -> Token:
        try:
            return self.tokens[self.cursor]
        except IndexError:
            raise SyntaxError("Unexpected end of file")

    @property
    def eof(self) -> bool:
        return self.cursor >= len(self.tokens)

    def next_not_space(self) -> Token:
        while not self.eof and self.at_cursor.token_type == TokenTypes.Space:
            self.inc_cursor()
        return self.at_cursor

    def peek_next_not_space(self) -> Token:
        cursor = self.cursor
        try:
            return self.next_not_space()
        finally:
            self.cursor = cursor


    def inc_cursor(self, amount: int = 1) -> None:
        self.cursor += amount

    def cursor_is_type(self, _type: TokenTypes) -> bool:
        return self.at_cursor.token_type == _type

    def consume(self, _type: TokenTypes) -> Token:
        _tmp = self.at_cursor
        if _tmp.token_type != _type:
            raise SyntaxError(f"Expected {_type}, got {_tmp.token_type} at position {_tmp.pos}")
        self.inc_cursor()
        return _tmp

    def consume_real(self, _type: TokenTypes) -> Token:
        self.next_not_space()
        return self.consume(_type)

    def parse(self) -> tuple[str, tuple[Any, ...], dict[str, Any]]:
        cmd = self.consume_real(TokenTypes.Identifier).value
        if self.eof:
            return cmd, (), {}
        self.consume(TokenTypes.Space)
        args, kwargs = [], {}
        while not self.eof:
            print(f"Cursor: {self.cursor}, EOF: {self.eof}\n{cmd=}\n{args=}")
            if self.kwargs:
                if not self.eof:
                    raise SyntaxError("Keyword arguments should be the last arguments.")
                break
            self.next_not_space()
            args.append(self.parse_sequence())
        if self.kwargs:
            kwargs = args.pop()
        return cmd, tuple(args), kwargs

    def parse_sequence(self):
        if not self.cursor_is_type(TokenTypes.OpenBracket) and not self.cursor_is_type(TokenTypes.OpenParen):
            return self.parse_dict()
        close = TokenTypes.CloseBracket if self.cursor_is_type(TokenTypes.OpenBracket) else TokenTypes.CloseParen
        self.inc_cursor()
        out = []
        while not self.eof and not self.cursor_is_type(close):
            out.append(self.parse_sequence())
            if self.cursor_is_type(TokenTypes.Comma):
                self.inc_cursor()
            else:
                break
        self.consume_real(close)
        return out if close == TokenTypes.CloseBracket else tuple(out)

    def parse_dict(self):
        if self.at_cursor.token_type != TokenTypes.OpenBrace:
            return self.parse_assignment()
        self.inc_cursor()
        out = {}
        while not self.eof and self.at_cursor.token_type != TokenTypes.CloseBrace:
            self.next_not_space()
            if self.at_cursor.token_type != TokenTypes.Identifier and self.at_cursor.token_type != TokenTypes.StringLiteral:
                break
            key = self.at_cursor.value
            self.inc_cursor()
            self.next_not_space()
            self.consume(TokenTypes.Colon)
            self.next_not_space()
            out[key] = self.parse_sequence()
            if self.at_cursor.token_type == TokenTypes.Comma:
                self.inc_cursor()
            else:
                break
        self.next_not_space()
        self.consume(TokenTypes.CloseBrace)
        return out

    def parse_assignment(self):
        if self.kwargs or not self.cursor_is_type(TokenTypes.Identifier):
            return self.parse_atom()
        elif self.peek_next_not_space().token_type != TokenTypes.Equal:
            _out = self.at_cursor.value
            self.inc_cursor()
            return _out
        self.kwargs = True
        kwargs = {}
        while not self.eof:
            if self.next_not_space().token_type != TokenTypes.Identifier:
                break
            key = self.consume(TokenTypes.Identifier).value
            self.consume_real(TokenTypes.Equal)
            kwargs[key] = self.parse_sequence()
        return kwargs

    def parse_atom(self):
        print(f"{self.at_cursor=}")
        match self.next_not_space().token_type:
            case TokenTypes.IntegerLiteral:
                out = int(self.at_cursor.value)
                self.inc_cursor()
                return out
            case TokenTypes.FloatingPointLiteral:
                out = float(self.at_cursor.value)
                self.inc_cursor()
                return out
            case TokenTypes.StringLiteral:
                out = self.at_cursor.value
                self.inc_cursor()
                return out
            case TokenTypes.BooleanLiteral:
                out = self.at_cursor.value == "True"
                self.inc_cursor()
                return out
            case _:
                raise SyntaxError(f"Unexpected: {self.at_cursor}")


if __name__ == '__main__':
    from rich import print
    raise_error = False
    parse_text = True
    while True:
        try:
            test = input(">>> ")
            if test == "raise":
                raise_error = not raise_error
                print(f"{raise_error=}")
                continue
            elif test == "parse":
                parse_text = not parse_text
                print(f"{parse_text=}")
                continue
            if not parse_text:
                print(Lexer(test).tokenize())
                continue
            else:
                print(Parser(test).parse())

        except Exception as e:
            if raise_error:
                raise e
            print(str(type(e))[8:-2], e, sep=": ")
