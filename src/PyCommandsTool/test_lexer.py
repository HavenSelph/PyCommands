import unittest
from typing import Any
from .lexer import *

VERBOSE = False


def lex(text: str) -> tuple[Token]:
    try:
        return Lexer(text, verbose=VERBOSE).tokenize()
    finally:
        if VERBOSE:
            print("\n")


def lex_then_unpack(text: str) -> tuple[tuple[str, ...], tuple[TokenTypes, ...]]:
    tokens = lex(text)
    return tuple(token.value for token in tokens), tuple(token.kind for token in tokens)


class TestLexerWithSingleTokens(unittest.TestCase):
    def test_integer_literal(self):
        self.assertEqual(("123",), lex_then_unpack("123")[0])
        self.assertEqual((TokenTypes.IntegerLiteral,), lex_then_unpack("123")[1])

    def test_integer_literal_with_spaces(self):
        self.assertEqual(("123",), lex_then_unpack(" 123 ")[0])
        self.assertEqual((TokenTypes.IntegerLiteral,), lex_then_unpack(" 123 ")[1])

    def test_integer_literal_with_spaces_before(self):
        self.assertEqual(("123",), lex_then_unpack(" 123")[0])
        self.assertEqual((TokenTypes.IntegerLiteral,), lex_then_unpack(" 123")[1])

    def test_integer_literal_with_spaces_after(self):
        self.assertEqual(("123",), lex_then_unpack("123 ")[0])
        self.assertEqual((TokenTypes.IntegerLiteral,), lex_then_unpack("123 ")[1])

    def test_floating_point_literal(self):
        self.assertEqual(("123.456",), lex_then_unpack("123.456")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack("123.456")[1])

    def test_floating_point_literal_with_spaces(self):
        self.assertEqual(("123.456",), lex_then_unpack(" 123.456 ")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack(" 123.456 ")[1])

    def test_floating_point_literal_with_spaces_before(self):
        self.assertEqual(("123.456",), lex_then_unpack(" 123.456")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack(" 123.456")[1])

    def test_floating_point_literal_with_spaces_after(self):
        self.assertEqual(("123.456",), lex_then_unpack("123.456 ")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack("123.456 ")[1])

    def test_floating_point_literal_with_leading_dot(self):
        self.assertEqual((".1",), lex_then_unpack(".1")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack(".1")[1])

    def test_floating_point_literal_with_leading_dot_and_spaces(self):
        self.assertEqual((".1",), lex_then_unpack(" .1 ")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack(" .1 ")[1])

    def test_floating_point_literal_with_trailing_dot(self):
        self.assertEqual(("1.",), lex_then_unpack("1.")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack("1.")[1])

    def test_floating_point_literal_with_trailing_dot_and_spaces(self):
        self.assertEqual(("1.",), lex_then_unpack(" 1. ")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral,), lex_then_unpack(" 1. ")[1])

    def test_string_literal(self):
        self.assertEqual(("hello",), lex_then_unpack('"hello"')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack('"hello"')[1])

    def test_string_literal_with_spaces(self):
        self.assertEqual(("hello",), lex_then_unpack(' "hello" ')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack(' "hello" ')[1])

    def test_string_literal_with_spaces_before(self):
        self.assertEqual(("hello",), lex_then_unpack(' "hello"')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack(' "hello"')[1])

    def test_string_literal_with_spaces_after(self):
        self.assertEqual(("hello",), lex_then_unpack('"hello" ')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack('"hello" ')[1])

    def test_string_literal_with_escaped_quotes(self):
        self.assertEqual(('hello "world"',), lex_then_unpack('"hello \\"world\\""')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack('"hello \\"world\\""')[1])

    def test_string_literal_with_escaped_quotes_and_spaces(self):
        self.assertEqual(('hello "world"',), lex_then_unpack(' "hello \\"world\\"" ')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack(' "hello \\"world\\"" ')[1])

    def test_string_literal_with_escaped_backslash(self):
        self.assertEqual(('hello \\world',), lex_then_unpack('"hello \\\\world"')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack('"hello \\\\world"')[1])

    def test_string_literal_with_escaped_backslash_and_spaces(self):
        self.assertEqual(('hello \\world',), lex_then_unpack(' "hello \\\\world" ')[0])
        self.assertEqual((TokenTypes.StringLiteral,), lex_then_unpack(' "hello \\\\world" ')[1])

    def test_colon(self):
        self.assertEqual((':',), lex_then_unpack(":")[0])
        self.assertEqual((TokenTypes.Colon,), lex_then_unpack(":")[1])

    def test_colon_with_spaces(self):
        self.assertEqual((':',), lex_then_unpack(" : ")[0])
        self.assertEqual((TokenTypes.Colon,), lex_then_unpack(" : ")[1])

    def test_colon_with_spaces_before(self):
        self.assertEqual((':',), lex_then_unpack(" :")[0])
        self.assertEqual((TokenTypes.Colon,), lex_then_unpack(" :")[1])

    def test_colon_with_spaces_after(self):
        self.assertEqual((':',), lex_then_unpack(": ")[0])
        self.assertEqual((TokenTypes.Colon,), lex_then_unpack(": ")[1])

    def test_comma(self):
        self.assertEqual((',',), lex_then_unpack(",")[0])
        self.assertEqual((TokenTypes.Comma,), lex_then_unpack(",")[1])

    def test_comma_with_spaces(self):
        self.assertEqual((',',), lex_then_unpack(" , ")[0])
        self.assertEqual((TokenTypes.Comma,), lex_then_unpack(" , ")[1])

    def test_comma_with_spaces_before(self):
        self.assertEqual((',',), lex_then_unpack(" ,")[0])
        self.assertEqual((TokenTypes.Comma,), lex_then_unpack(" ,")[1])

    def test_comma_with_spaces_after(self):
        self.assertEqual((',',), lex_then_unpack(", ")[0])
        self.assertEqual((TokenTypes.Comma,), lex_then_unpack(", ")[1])

    def test_open_brace(self):
        self.assertEqual(('{',), lex_then_unpack("{")[0])
        self.assertEqual((TokenTypes.OpenBrace,), lex_then_unpack("{")[1])

    def test_open_brace_with_spaces(self):
        self.assertEqual(('{',), lex_then_unpack(" { ")[0])
        self.assertEqual((TokenTypes.OpenBrace,), lex_then_unpack(" { ")[1])

    def test_open_brace_with_spaces_before(self):
        self.assertEqual(('{',), lex_then_unpack(" {")[0])
        self.assertEqual((TokenTypes.OpenBrace,), lex_then_unpack(" {")[1])

    def test_open_brace_with_spaces_after(self):
        self.assertEqual(('{',), lex_then_unpack("{ ")[0])
        self.assertEqual((TokenTypes.OpenBrace,), lex_then_unpack("{ ")[1])

    def test_close_brace(self):
        self.assertEqual(('}',), lex_then_unpack("}")[0])
        self.assertEqual((TokenTypes.CloseBrace,), lex_then_unpack("}")[1])

    def test_close_brace_with_spaces(self):
        self.assertEqual(('}',), lex_then_unpack(" } ")[0])
        self.assertEqual((TokenTypes.CloseBrace,), lex_then_unpack(" } ")[1])

    def test_close_brace_with_spaces_before(self):
        self.assertEqual(('}',), lex_then_unpack(" }")[0])
        self.assertEqual((TokenTypes.CloseBrace,), lex_then_unpack(" }")[1])

    def test_close_brace_with_spaces_after(self):
        self.assertEqual(('}',), lex_then_unpack("} ")[0])
        self.assertEqual((TokenTypes.CloseBrace,), lex_then_unpack("} ")[1])

    def test_open_bracket(self):
        self.assertEqual(('[',), lex_then_unpack("[")[0])
        self.assertEqual((TokenTypes.OpenBracket,), lex_then_unpack("[")[1])

    def test_open_bracket_with_spaces(self):
        self.assertEqual(('[',), lex_then_unpack(" [ ")[0])
        self.assertEqual((TokenTypes.OpenBracket,), lex_then_unpack(" [ ")[1])

    def test_open_bracket_with_spaces_before(self):
        self.assertEqual(('[',), lex_then_unpack(" [")[0])
        self.assertEqual((TokenTypes.OpenBracket,), lex_then_unpack(" [")[1])

    def test_open_bracket_with_spaces_after(self):
        self.assertEqual(('[',), lex_then_unpack("[ ")[0])
        self.assertEqual((TokenTypes.OpenBracket,), lex_then_unpack("[ ")[1])

    def test_close_bracket(self):
        self.assertEqual((']',), lex_then_unpack("]")[0])
        self.assertEqual((TokenTypes.CloseBracket,), lex_then_unpack("]")[1])

    def test_close_bracket_with_spaces(self):
        self.assertEqual((']',), lex_then_unpack(" ] ")[0])
        self.assertEqual((TokenTypes.CloseBracket,), lex_then_unpack(" ] ")[1])

    def test_close_bracket_with_spaces_before(self):
        self.assertEqual((']',), lex_then_unpack(" ]")[0])
        self.assertEqual((TokenTypes.CloseBracket,), lex_then_unpack(" ]")[1])

    def test_close_bracket_with_spaces_after(self):
        self.assertEqual((']',), lex_then_unpack("] ")[0])
        self.assertEqual((TokenTypes.CloseBracket,), lex_then_unpack("] ")[1])

    def test_boolean_true(self):
        self.assertEqual(('True',), lex_then_unpack("True")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack("True")[1])

    def test_boolean_true_with_spaces(self):
        self.assertEqual(('True',), lex_then_unpack(" True ")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack(" True ")[1])

    def test_boolean_true_with_spaces_before(self):
        self.assertEqual(('True',), lex_then_unpack(" True")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack(" True")[1])

    def test_boolean_true_with_spaces_after(self):
        self.assertEqual(('True',), lex_then_unpack("True ")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack("True ")[1])

    def test_boolean_false(self):
        self.assertEqual(('False',), lex_then_unpack("False")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack("False")[1])

    def test_boolean_false_with_spaces(self):
        self.assertEqual(('False',), lex_then_unpack(" False ")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack(" False ")[1])

    def test_boolean_false_with_spaces_before(self):
        self.assertEqual(('False',), lex_then_unpack(" False")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack(" False")[1])

    def test_boolean_false_with_spaces_after(self):
        self.assertEqual(('False',), lex_then_unpack("False ")[0])
        self.assertEqual((TokenTypes.BooleanLiteral,), lex_then_unpack("False ")[1])

    def test_none_literal(self):
        self.assertEqual(('None',), lex_then_unpack("None")[0])
        self.assertEqual((TokenTypes.NoneLiteral,), lex_then_unpack("None")[1])

    def test_none_literal_with_spaces(self):
        self.assertEqual(('None',), lex_then_unpack(" None ")[0])
        self.assertEqual((TokenTypes.NoneLiteral,), lex_then_unpack(" None ")[1])

    def test_none_literal_with_spaces_before(self):
        self.assertEqual(('None',), lex_then_unpack(" None")[0])
        self.assertEqual((TokenTypes.NoneLiteral,), lex_then_unpack(" None")[1])

    def test_none_literal_with_spaces_after(self):
        self.assertEqual(('None',), lex_then_unpack("None ")[0])
        self.assertEqual((TokenTypes.NoneLiteral,), lex_then_unpack("None ")[1])


class TestLexerWithMultipleTokens(unittest.TestCase):
    def test_multiple_integers(self):
        self.assertEqual(('123', '456', '789'), lex_then_unpack("123 456 789")[0])
        self.assertEqual((TokenTypes.IntegerLiteral, TokenTypes.IntegerLiteral, TokenTypes.IntegerLiteral),
                         lex_then_unpack("123 456 789")[1])

    def test_multiple_integers_with_spaces(self):
        self.assertEqual(('123', '456', '789'), lex_then_unpack(" 123 456 789 ")[0])
        self.assertEqual((TokenTypes.IntegerLiteral, TokenTypes.IntegerLiteral, TokenTypes.IntegerLiteral),
                         lex_then_unpack(" 123 456 789 ")[1])

    def test_multiple_floats(self):
        self.assertEqual(('123.456', '789.012'), lex_then_unpack("123.456 789.012")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral, TokenTypes.FloatingPointLiteral),
                         lex_then_unpack("123.456 789.012")[1])

    def test_multiple_floats_with_spaces(self):
        self.assertEqual(('123.456', '789.012'), lex_then_unpack(" 123.456 789.012 ")[0])
        self.assertEqual((TokenTypes.FloatingPointLiteral, TokenTypes.FloatingPointLiteral),
                         lex_then_unpack(" 123.456 789.012 ")[1])

    def test_multiple_strings(self):
        self.assertEqual(('hello', 'world'), lex_then_unpack('"hello" "world"')[0])
        self.assertEqual((TokenTypes.StringLiteral, TokenTypes.StringLiteral),
                         lex_then_unpack('"hello" "world"')[1])

    def test_multiple_strings_with_spaces(self):
        self.assertEqual(('hello', 'world'), lex_then_unpack(' "hello" "world" ')[0])
        self.assertEqual((TokenTypes.StringLiteral, TokenTypes.StringLiteral),
                         lex_then_unpack(' "hello" "world" ')[1])

    def test_multiple_booleans(self):
        self.assertEqual(('True', 'False'), lex_then_unpack("True False")[0])
        self.assertEqual((TokenTypes.BooleanLiteral, TokenTypes.BooleanLiteral),
                         lex_then_unpack("True False")[1])

    def test_multiple_booleans_with_spaces(self):
        self.assertEqual(('True', 'False'), lex_then_unpack(" True False ")[0])
        self.assertEqual((TokenTypes.BooleanLiteral, TokenTypes.BooleanLiteral),
                         lex_then_unpack(" True False ")[1])

    def test_multiple_nones(self):
        self.assertEqual(('None', 'None'), lex_then_unpack("None None")[0])
        self.assertEqual((TokenTypes.NoneLiteral, TokenTypes.NoneLiteral),
                         lex_then_unpack("None None")[1])

    def test_multiple_nones_with_spaces(self):
        self.assertEqual(('None', 'None'), lex_then_unpack(" None None ")[0])
        self.assertEqual((TokenTypes.NoneLiteral, TokenTypes.NoneLiteral),
                         lex_then_unpack(" None None ")[1])

    def test_multiple_identifiers(self):
        self.assertEqual(('foo', 'bar'), lex_then_unpack("foo bar")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack("foo bar")[1])

    def test_multiple_identifiers_with_spaces(self):
        self.assertEqual(('foo', 'bar'), lex_then_unpack(" foo bar ")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack(" foo bar ")[1])

    def test_multiple_identifiers_with_underscores(self):
        self.assertEqual(('foo_bar', 'bar_foo'), lex_then_unpack("foo_bar bar_foo")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack("foo_bar bar_foo")[1])

    def test_multiple_identifiers_with_underscores_and_spaces(self):
        self.assertEqual(('foo_bar', 'bar_foo'), lex_then_unpack(" foo_bar bar_foo ")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack(" foo_bar bar_foo ")[1])

    def test_multiple_identifiers_with_numbers(self):
        self.assertEqual(('foo123', 'bar456'), lex_then_unpack("foo123 bar456")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack("foo123 bar456")[1])

    def test_multiple_identifiers_with_numbers_and_spaces(self):
        self.assertEqual(('foo123', 'bar456'), lex_then_unpack(" foo123 bar456 ")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack(" foo123 bar456 ")[1])

    def test_multiple_identifiers_with_numbers_and_underscores(self):
        self.assertEqual(('foo_123', 'bar_456'), lex_then_unpack("foo_123 bar_456")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack("foo_123 bar_456")[1])

    def test_multiple_identifiers_with_numbers_and_underscores_and_spaces(self):
        self.assertEqual(('foo_123', 'bar_456'), lex_then_unpack(" foo_123 bar_456 ")[0])
        self.assertEqual((TokenTypes.Identifier, TokenTypes.Identifier),
                         lex_then_unpack(" foo_123 bar_456 ")[1])

    def test_multiple_of_all(self):
        self.assertEqual(('{', '[', '(', ',', ':', '1', '2.3', 'a', "b", 'c', 'True', 'False', 'None'),
                         lex_then_unpack("{[(,: 1 2.3 a 'b' \"c\" True False None")[0])
        self.assertEqual((TokenTypes.OpenBrace, TokenTypes.OpenBracket, TokenTypes.OpenParenthesis,
                          TokenTypes.Comma, TokenTypes.Colon, TokenTypes.IntegerLiteral,
                          TokenTypes.FloatingPointLiteral, TokenTypes.Identifier, TokenTypes.StringLiteral,
                          TokenTypes.StringLiteral, TokenTypes.BooleanLiteral, TokenTypes.BooleanLiteral,
                          TokenTypes.NoneLiteral), lex_then_unpack("{[(,: 1 2.3 a 'b' \"c\" True False None")[1])

    def test_multiple_of_all_with_spaces(self):
        self.assertEqual(('{', '[', '(', ',', ':', '1', '2.3', 'a', "b", 'c', 'True', 'False', 'None'),
                         lex_then_unpack(" { [ ( , : 1 2.3 a 'b' \"c\" True False None ")[0])
        self.assertEqual((TokenTypes.OpenBrace, TokenTypes.OpenBracket, TokenTypes.OpenParenthesis,
                          TokenTypes.Comma, TokenTypes.Colon, TokenTypes.IntegerLiteral,
                          TokenTypes.FloatingPointLiteral, TokenTypes.Identifier, TokenTypes.StringLiteral,
                          TokenTypes.StringLiteral, TokenTypes.BooleanLiteral, TokenTypes.BooleanLiteral,
                          TokenTypes.NoneLiteral), lex_then_unpack(" { [ ( , : 1 2.3 a 'b' \"c\" True False None ")[1])


class TestLexerExpectedFailures(unittest.TestCase):
    def test_float_with_multiple_dots(self):
        with self.assertRaises(SyntaxError):
            lex("123.456.789")

    def test_float_with_multiple_dots_and_spaces(self):
        with self.assertRaises(SyntaxError):
            lex(" 123.456.789 ")

    def test_string_literal_with_no_closing_quote(self):
        with self.assertRaises(SyntaxError):
            lex('"hello')

    def test_string_literal_with_no_closing_quote_and_spaces(self):
        with self.assertRaises(SyntaxError):
            lex(' "hello')

    def test_single_dot(self):
        with self.assertRaises(SyntaxError):
            lex(".")

    def test_single_dot_with_spaces(self):
        with self.assertRaises(SyntaxError):
            lex(" . ")

    def test_single_dot_with_spaces_before(self):
        with self.assertRaises(SyntaxError):
            lex(" .")

    def test_single_dot_with_spaces_after(self):
        with self.assertRaises(SyntaxError):
            lex(". ")
