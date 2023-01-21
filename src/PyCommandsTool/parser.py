import re


def parse(text: str, protected: bool=False, debug=False) -> tuple[list, dict]:
    keywords = {}

    def helper(_token: dict) -> any:
        if debug:
            print(f"Found a {_token['type']}")
        match _token:
            case {"type": "word"}:
                return _token["value"]
            case {"type": "string"}:
                return _token["value"]
            case {"type": "float"}:
                return float(_token["value"])
            case {"type": "integer"}:
                return int(_token["value"])
            case {"type": "list"}:
                return [helper(_tkn) for _tkn in _token["value"]]
            case {"type": "tuple"}:
                return tuple([helper(_tkn) for _tkn in _token["value"]])
            case {"type": "dict"}:
                return {_tkn["left"]: helper(_tkn["right"]) for _tkn in _token["value"]}
            case {"type": "assignment"}:
                keywords[_token["left"]] = helper(_token["right"])

    if debug:
        print(f"Parsing string: {text}")

    _Tokenizer = Tokenizer(text)
    _out = []
    try:
        if debug:
            print("Getting all tokens")
        token = _Tokenizer.getNextToken()

        while token["type"] != "EOF":
            if debug:
                print(f"Got Token: {token}")
            _out.append(helper(token))
            token = _Tokenizer.getNextToken()
        if debug:
            print(f"Returning: {_out}", end="\n\n")
        return _out, keywords
    except Tokenizer.UnexpectedToken as e:
        if debug:
            print(e)
        if protected:
            return [],{}
        else:
            raise e
    except Tokenizer.UnexpectedEOF as e:
        if debug:
            print(e)
        if protected:
            return [],{}
        else:
            raise e


class Tokenizer:
    class UnexpectedEOF(Exception):
        pass

    class UnexpectedToken(Exception):
        pass

    def __init__(self, text: str) -> None:
        """Initializes tokenizer with text"""
        self.text = text
        self._cursor = 0

    @property
    def notEOF(self) -> bool:
        """Returns True if not at end of file"""
        return self._cursor<len(self.text)

    @property
    def cursor(self) -> int:
        """Returns current cursor position"""
        return self._cursor

    @property
    def atCursor(self) -> str:
        """Returns current character at cursor"""
        if self.notEOF:
            return self.text[self._cursor]
        else:
            return ""

    @property
    def fromCursor(self) -> str:
        """Returns text from cursor"""
        return self.text[self._cursor:]

    def matchCursor(self, exp: str) -> bool:
        """Returns True if cursor matches exp"""
        return re.match(exp, self.atCursor) is not None

    def mvCursor(self, i: int=1) -> int:
        """Moves cursor by i and returns new cursor position"""
        self._cursor += i
        return self.cursor

    def consume(self, exp=r"\s") -> str:
        """Returns next character that doesn't match exp"""
        while re.match(exp, self.atCursor):
            self.mvCursor()
        return self.atCursor

    def getNextToken(self) -> dict:  # Recursive Descent Parser
        """Returns next token"""

        while self.notEOF:  # While not at end of file
            self.consume()
            if not self.notEOF:
                return {"type": "EOF", "value": None}
            if self.matchCursor(r"[a-zA-Z]"):  # WORD
                _out = ""
                while self.notEOF and not self.matchCursor(r"\s"):
                    if self.matchCursor(r"[a-zA-Z]|[0-9]"):  # Checks if character is a letter or number
                        _out += self.atCursor
                        self.mvCursor()
                    elif self.matchCursor(r"="):  # Checks if character is an assignment
                        self.mvCursor()
                        _tmp = self.getNextToken()
                        if _tmp["type"] in ("float", "integer", "string", "list", "tuple", "dict"):  # If token is of valid type
                            return {"type": "assignment", "left": _out, "right": _tmp}
                        elif _tmp["type"] == "EOF":  # If token is EOF raise error
                            raise self.UnexpectedEOF("Unexpected EOF")
                        else:  # If token is invalid raise error
                            raise self.UnexpectedToken(f"Unexpected token '{self.atCursor}'")
                    elif self.matchCursor(r":"):  # Checks if character is a dictionary
                        self.mvCursor()
                        _tmp = self.getNextToken()
                        if _tmp["type"] in ("float", "integer", "string", "list", "tuple", "dict"):  # If token is of valid type
                            return {"type": "dict-assignment", "left": _out, "right": _tmp}
                        else:  # If token is invalid raise error
                            raise self.UnexpectedToken(f"Unexpected token '{self.atCursor}'")
                    else:  # If character is not valid raise error
                        raise self.UnexpectedToken(f"Unexpected character '{self.atCursor}'")
                self.mvCursor()
                return {"type": "word", "value": _out}
            elif self.matchCursor(r"[0-9]"):  # NUMBER
                _out = ""
                while self.notEOF and self.matchCursor(r"[0-9]|\."):
                    if self.matchCursor(r"[0-9]"):  # Checks if character is a number
                        _out += self.atCursor
                        self.mvCursor()
                    elif self.matchCursor(r"\."):  # Checks if character is a decimal
                        if "." in _out:  # Checks if there is already a decimal
                            raise self.UnexpectedToken(f"Invalid number '{self.atCursor}'")
                        _out += self.atCursor
                        self.mvCursor()
                    else:  # If character is not valid raise error
                        raise self.UnexpectedToken(f"Unexpected character '{self.atCursor}'")
                return {"type": "float" if "." in _out else "integer", "value": float(_out) if "." in _out else int(_out)}
            elif self.matchCursor(r"\"|\'"):  # STRING
                _out = ""
                _quote = self.atCursor
                self.mvCursor()
                while self.atCursor != _quote:  # Until character is a closing quote
                    if not self.notEOF:  # If at end of file raise error
                        raise self.UnexpectedEOF("Unexpected EOF")
                    if self.matchCursor(r"\\"):  # Checks if character is an escape character
                        self.mvCursor()
                        if self.matchCursor('n'):  # Checks if character is a newline
                            raise self.UnexpectedToken("Unexpected character '\\n'")
                    _out += self.atCursor
                    self.mvCursor()
                self.mvCursor()
                return {"type": "string", "value": _out}

            elif self.matchCursor(r"\("):  # TUPLE
                self.mvCursor()
                self.consume(" ")
                _out = [self.getNextToken()]
                while not self.matchCursor(r"\)"):  # Until character is a closing parenthesis
                    self.consume(" ")
                    if not self.notEOF:  # If at end of file raise error
                        raise self.UnexpectedToken("Unexpected EOF")
                    if self.matchCursor(r","):
                        self.mvCursor()
                        _tmp = self.getNextToken()
                        if _tmp["type"] in ("float", "integer", "string", "list", "tuple", "dict"):  # If token is of valid type
                            _out.append(_tmp)
                        else:  # If token is invalid raise error
                            raise self.UnexpectedToken(f"Unexpected token '{_tmp['type']}'")
                    else:
                        raise self.UnexpectedToken(f"Unexpected character '{self.atCursor}'")
                self.mvCursor()
                return {"type": "tuple", "value": _out}

            elif self.matchCursor(r"\["):  # LIST
                self.mvCursor()
                self.consume(" ")
                _out = [self.getNextToken()]
                while not self.matchCursor(r"\]"):  # Until character is a closing bracket
                    self.consume(" ")
                    if not self.notEOF:  # If at end of file raise error
                        raise self.UnexpectedEOF("Unexpected EOF")
                    if self.matchCursor(r","):
                        self.mvCursor()
                        _tmp = self.getNextToken()
                        if _tmp["type"] in ("float", "integer", "string", "list", "tuple", "dict"):  # If token is invalid raise error
                            _out.append(_tmp)
                        else:  # If token is invalid raise error
                            raise self.UnexpectedToken(f"Unexpected token '{_tmp['type']}'")
                    else:
                        raise self.UnexpectedToken(f"Unexpected character '{self.atCursor}'")
                self.mvCursor()
                return {"type": "list", "value": _out}

            elif self.matchCursor(r"\{"):  # DICTIONARY
                self.mvCursor()
                self.consume(" ")
                _out = [self.getNextToken()]
                while not self.matchCursor(r"\}"):  # Until character is a closing brace
                    self.consume(" ")
                    if not self.notEOF:  # If at end of file raise error
                        raise self.UnexpectedEOF("Unexpected EOF")
                    if self.matchCursor(r","):
                        self.mvCursor()
                        _tmp = self.getNextToken()
                        if _tmp["type"]=="dict-assignment":
                            _out.append(_tmp)
                        else:  # If token is not dict-assignment raise error
                            raise self.UnexpectedToken(f"Unexpected token '{_tmp['type']}'")
                    else:
                        raise self.UnexpectedToken(f"Unexpected character '{self.atCursor}'")
                self.mvCursor()
                return {"type": "dict", "value": _out}

            else:  # If character is not valid raise error
                raise self.UnexpectedToken(f"Unexpected character '{self.atCursor}'")
        return {"type": "EOF", "value": None}
