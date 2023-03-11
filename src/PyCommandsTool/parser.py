if __name__ == "__main__":
    from lexer import Lexer, TokenTypes, Token
else:
    from .lexer import Lexer, TokenTypes, Token
from typing import Any


class Parser:
    def __init__(self, text: str, verbose: bool = False, raise_errors: bool = True) -> None:
        self.text = text
        self.verbose = verbose
        self.raise_errors = raise_errors
        self.cursor = 0
        self.tokens = []
        self.kwargs = False
        self.lexer = Lexer(text, verbose=verbose, raise_errors=raise_errors)
        if not self.raise_errors:
            self.verbose = True
        self.log(f"Initializing Parser with text: {text!r}, {verbose=}, {raise_errors=}", caller="__init__")
        self.log(
            f"Running the lexer with raise_errors disabled is not recommended, as it can leave the parser in an unstable state.",
            caller="WARNING", error=True)

    def log(self, *args, caller: str = None, error: bool = False, **kwargs) -> None:
        if self.verbose:
            color = "\u001b[31m" if error else ""
            print(f"{color}[Parser] {caller if caller else ''}", *args, **kwargs, sep=" ", end="\u001b[0m\n")

    def raise_error(self, error, msg: str, point_text: str, override=None) -> None:
        if override is not None:
            cursor = override
            start = override
        else:
            cursor = self.current_token.pos_end
            start = self.current_token.pos_start
        pos = f"{start}:{cursor}" if start != cursor else cursor
        out = f"[Parser] {error.__name__}: {msg} at index {pos}\n{self.text}"
        out += "\n" + " " * (override if override is not None else start) + "^" * (
                    cursor - start + 1) + f" {point_text}"
        raise error(out)

    @property
    def eof(self) -> bool:
        return self.cursor >= len(self.tokens)

    @property
    def current_token(self) -> Token:
        return self.tokens[self.cursor]

    def is_kind(self, kind: TokenTypes) -> bool:
        return self.current_token.kind == kind

    def advance(self) -> None:
        self.cursor += 1

    def consume(self, kind: TokenTypes) -> Token:
        try:
            _token = self.current_token
        except IndexError:
            self.raise_error(SyntaxError, f"Expected {kind.name} but got EOF", "Expected a token here.",
                             override=len(self.text) + 1)
        if self.current_token.kind == kind:
            self.log(f"Consumed {kind.name} token: {self.current_token.value!r}", caller="consume")
            self.advance()
            return _token
        self.raise_error(SyntaxError, f"Expected {kind.name} but got {_token.kind}", f"Expected {kind.name}")

    def parse(self) -> tuple[str, tuple[Any, ...], dict[str | int, Any]]:
        self.tokens = self.lexer.tokenize()
        tokens = '\n'.join([repr(token) for token in self.tokens])
        self.log(f"Tokens: [\n{tokens}\n]", caller="parse")
        cmd = self.consume(TokenTypes.Identifier).value
        args = []
        kwargs = {}
        while not self.eof:
            if not self.current_token.space_before:
                self.raise_error(SyntaxError, f"Unexpected token: {self.current_token.kind}", "expected a space.")
            args.append(self.parse_sequence())
            self.log(f"Found argument: {args[-1]}", caller="parse")
        if self.kwargs:
            self.log(f"Found keyword arguments: {self.tokens[-1]}", caller="parse")
            kwargs = args.pop()
        self.log(f"Found command: {cmd=!r}, {args=}, {kwargs=}", caller="parse")
        return cmd, tuple(args), kwargs

    def parse_sequence(self) -> Any:
        if not (self.is_kind(TokenTypes.OpenBracket) or self.is_kind(TokenTypes.OpenParenthesis)):
            return self.parse_dict()
        close = TokenTypes.CloseBracket if self.is_kind(TokenTypes.OpenBracket) else TokenTypes.CloseParenthesis
        out = []
        self.advance()
        while not self.eof and not self.is_kind(close):
            out.append(self.parse_sequence())
            if self.is_kind(TokenTypes.Comma):
                self.advance()
        self.log(f"Found list: {out}", caller="parse_sequence")
        self.advance()
        return tuple(out) if close == TokenTypes.CloseParenthesis else out

    def parse_dict(self) -> Any:
        if not self.is_kind(TokenTypes.OpenBrace):
            return self.parse_assignment()
        out = {}
        self.advance()
        while not self.eof and not self.is_kind(TokenTypes.CloseBrace):
            key = self.parse_atom()
            self.consume(TokenTypes.Colon)
            out[key] = self.parse_sequence()
            if self.is_kind(TokenTypes.Comma):
                self.advance()
        self.log(f"Found dictionary: {out}", caller="parse_dict")
        self.advance()
        return out

    def parse_assignment(self) -> Any:
        if self.cursor >= len(self.tokens) - 1 or not (self.is_kind(TokenTypes.Identifier) and self.tokens[
            self.cursor + 1].kind == TokenTypes.Equal) or self.kwargs:
            return self.parse_atom()
        self.kwargs = True
        kwargs = {}
        while not self.eof:
            key = self.consume(TokenTypes.Identifier).value
            self.consume(TokenTypes.Equal)
            kwargs[key] = self.parse_sequence()
        self.log(f"Found keyword arguments: {kwargs}", caller="parse_assignment")
        return kwargs

    def parse_atom(self) -> Any:
        match self.current_token.kind:
            case TokenTypes.StringLiteral:
                self.log(f"Found string literal: {self.current_token.value!r}", caller="parse_atom")
                _out = self.current_token.value
                self.advance()
                return _out
            case TokenTypes.Identifier:
                self.log(f"Found identifier: {self.current_token.value!r}, parsing as string literal",
                         caller="parse_atom")
                _out = self.current_token.value
                self.advance()
                return _out
            case TokenTypes.IntegerLiteral:
                self.log(f"Found integer literal: {self.current_token.value!r}", caller="parse_atom")
                _out = int(self.current_token.value)
                self.advance()
                return _out
            case TokenTypes.FloatingPointLiteral:
                self.log(f"Found floating point literal: {self.current_token.value!r}", caller="parse_atom")
                _out = float(self.current_token.value)
                self.advance()
                return _out
            case TokenTypes.BooleanLiteral:
                self.log(f"Found boolean literal: {self.current_token.value!r}", caller="parse_atom")
                _out = self.current_token.value == "True"
                self.advance()
                return _out
            case TokenTypes.NoneLiteral:
                self.log(f"Found None literal: {self.current_token.value!r}", caller="parse_atom")
                self.advance()
                return None
            case token:
                self.raise_error(SyntaxError, f"Unexpected token: {token}", "is not valid here")

    def __repr__(self):
        return f"Parser({self.text!r}, {self.verbose=}, {self.raise_errors=})"


if __name__ == '__main__':
    from rich import print

    raise_error = False
    parse_text = True
    verbose = True
    while True:
        test = input(">>> ")
        if test == "raise":
            raise_error = not raise_error
            print(f"{raise_error=}")
            continue
        elif test == "parse":
            parse_text = not parse_text
            print(f"{parse_text=}")
            continue
        elif test == "verbose":
            verbose = not verbose
            print(f"{verbose=}")
            continue
        if not parse_text:
            print(Lexer(test, verbose, raise_error).tokenize())
        else:
            print(Parser(test, verbose, raise_error).parse())
