from enum import Enum, auto
from typing import Any


class TokenTypes(Enum):
    # Literals
    StringLiteral = auto()  # "Hello World"
    IntegerLiteral = auto()  # 1
    FloatingPointLiteral = auto()  # 1.0
    BooleanLiteral = auto()  # True or False
    NoneLiteral = auto()  # None

    # Characters
    OpenParenthesis = auto()  # (
    CloseParenthesis = auto()  # )
    OpenBracket = auto()  # [
    CloseBracket = auto()  # ]
    OpenBrace = auto()  # {
    CloseBrace = auto()  # }
    Comma = auto()  # ,
    Colon = auto()  # :
    Equal = auto()  # =

    # Misc
    Identifier = auto()  # hello


keywords = {
    "True": TokenTypes.BooleanLiteral,
    "False": TokenTypes.BooleanLiteral,
    "None": TokenTypes.NoneLiteral
}

characters = {
    "(": TokenTypes.OpenParenthesis,
    ")": TokenTypes.CloseParenthesis,
    "[": TokenTypes.OpenBracket,
    "]": TokenTypes.CloseBracket,
    "{": TokenTypes.OpenBrace,
    "}": TokenTypes.CloseBrace,
    ",": TokenTypes.Comma,
    ":": TokenTypes.Colon,
    "=": TokenTypes.Equal
}


class Token:
    def __init__(self, kind: TokenTypes, value: Any, pos_start: int, pos_end: int, space_before: bool = False,
                 space_after: bool = False) -> None:
        self.kind = kind
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.space_before = space_before
        self.space_after = space_after

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.value!r}, {self.pos_start}:{self.pos_end}, {self.space_before=}, {self.space_after=})"


class Lexer:
    def __init__(self, text: str, verbose: bool = False, raise_errors: bool = True) -> None:
        self.cursor = 0
        self.tokens = []
        self.text = text
        self.verbose = verbose
        self.raise_errors = raise_errors
        if not self.raise_errors:
            self.verbose = True
            self.log(f"Running with raise_errors disabled.", caller="__init__")
        self.log(f"Initializing Lexer with text: {text!r}, {verbose=}", caller="__init__")

    def log(self, *args, caller: str = None, error: bool = False, **kwargs) -> None:
        if self.verbose:
            color = "\u001b[31m" if error else ""
            print(f"{color}[Lexer] {caller if caller else ''}", *args, **kwargs, sep=" ", end="\u001b[0m\n")

    def raise_error(self, error, msg: str, point_text, start: int = None) -> None:
        start = self.cursor if start is None else start
        pos = f"{start}:{self.cursor}" if start != self.cursor else self.cursor
        out = f"[Lexer] {error.__name__}: {msg} at index {pos}\n{self.text}"
        out += "\n" + " " * start + "^" * (self.cursor - start + 1) + f" {point_text}"
        if self.raise_errors:
            raise error(out)
        else:
            self.log(out, error=True)

    @property
    def at_cursor(self) -> str:
        return self.text[self.cursor]

    @property
    def eof(self) -> bool:
        return self.cursor >= len(self.text)

    def advance_cursor(self, amount: int = 1):
        self.cursor += amount

    def tokenize(self) -> tuple[Token, ...]:
        def push_token(token: TokenTypes, value: str, _start: int = None) -> None:
            _start = self.cursor - 1 if _start is None else _start
            _token = Token(token, value, _start, self.cursor - 1, space_before(_start))
            self.log(f"Pushing token: {_token}", caller="push_token")
            self.tokens.append(_token)

        def space_before(_start: int = None) -> bool:
            _start = self.cursor if _start is None else _start
            self.log(f"Checking if there is a space before index {_start} ({self.text[_start]!r})", caller="tokenize")
            if _start - 1 < 0:
                return False
            return self.text[_start - 1].isspace()

        self.log("Started tokenizer", caller="tokenize")
        while not self.eof:
            match self.at_cursor:
                case char if char.isalpha():
                    self.log(f"Found letter at index {self.cursor} ({self.at_cursor!r})", caller="tokenize")
                    start = self.cursor
                    out = ""
                    while not self.eof and (self.at_cursor.isalnum() or self.at_cursor == "_"):
                        out += self.at_cursor
                        self.advance_cursor()
                    push_token(keywords.get(out, TokenTypes.Identifier), out, start)
                case char if char == "'" or char == '"':
                    self.log(f"Found string literal at index {self.cursor} ({self.at_cursor!r})", caller="tokenize")
                    start = self.cursor
                    out = ""
                    self.advance_cursor()
                    while not self.eof and (self.at_cursor != char or self.text[self.cursor - 1] == "\\"):
                        if self.at_cursor == "\\" and self.text[self.cursor - 1] != "\\":
                            self.advance_cursor()
                            continue
                        out += self.at_cursor
                        self.advance_cursor()
                    if self.eof:
                        self.cursor -= 1
                        self.raise_error(SyntaxError, f"Invalid string literal", f"String literal was not closed.",
                                         start)
                    self.advance_cursor()
                    push_token(TokenTypes.StringLiteral, out, start)
                case char if char.isdigit() or char == ".":
                    self.log(f"Found integer/float at index {self.cursor} ({self.at_cursor!r})", caller="tokenize")
                    start = self.cursor
                    out = ""
                    while not self.eof and (self.at_cursor.isdigit() or self.at_cursor == "."):
                        if self.at_cursor == "." and "." in out:
                            self.raise_error(SyntaxError, f"Invalid floating point literal",
                                             f"Floating point literal cannot have more than one dot.", start)
                        out += self.at_cursor
                        self.advance_cursor()
                    if out == ".":
                        self.cursor -= 1
                        self.raise_error(SyntaxError, f"Unexpected character", f"is not a valid character", start)
                    push_token(TokenTypes.FloatingPointLiteral if "." in out else TokenTypes.IntegerLiteral, out, start)
                case char if char in characters:
                    self.advance_cursor()
                    push_token(characters[char], char)
                case char if char.isspace():
                    if self.tokens and not self.tokens[-1].space_after:
                        self.log(f"Found space at index {self.cursor}, updating last token ({self.tokens[-1]})",
                                 caller="tokenize")
                        self.tokens[-1].space_after = True
                    else:
                        self.log(f"Found space at index {self.cursor}, skipping", caller="tokenize")
                    self.advance_cursor()
                case _:
                    self.raise_error(SyntaxError, "Unexpected character",
                                     f"{self.at_cursor!r} is not a valid character")
                    self.advance_cursor()
        self.log("Finished tokenization", caller="tokenize")
        return tuple(self.tokens)

    def __repr__(self):
        return f"Lexer({self.text!r}, {self.verbose=}, {self.raise_errors=})"
