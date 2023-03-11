import unittest
from typing import Any
from .parser import *

VERBOSE = False


def parse(text: str) -> tuple[str, tuple[Any, ...], dict[str | int, Any]]:
    cmd, args, kwargs = Parser(text, verbose=VERBOSE).parse()
    return cmd, args, kwargs


class TestParserWithSingleTokens(unittest.TestCase):
    def test_identifier(self):
        cmd, args, kwargs = parse("test")
        self.assertEqual("test", cmd)
        self.assertEqual((), args)
        self.assertEqual({}, kwargs)

    def test_number(self):
        cmd, args, kwargs = parse("cmd 1")
        self.assertEqual("cmd", cmd)
        self.assertEqual((1,), args)
        self.assertEqual({}, kwargs)

    def test_float(self):
        cmd, args, kwargs = parse("cmd 1.0")
        self.assertEqual("cmd", cmd)
        self.assertEqual((1.0,), args)
        self.assertEqual({}, kwargs)

    def test_bool(self):
        cmd, args, kwargs = parse("cmd True")
        self.assertEqual("cmd", cmd)
        self.assertEqual((True,), args)
        self.assertEqual({}, kwargs)

        cmd, args, kwargs = parse("cmd False")
        self.assertEqual("cmd", cmd)
        self.assertEqual((False,), args)
        self.assertEqual({}, kwargs)

    def test_none(self):
        cmd, args, kwargs = parse("cmd None")
        self.assertEqual("cmd", cmd)
        self.assertEqual((None,), args)
        self.assertEqual({}, kwargs)

    def test_list(self):
        cmd, args, kwargs = parse("cmd []")
        self.assertEqual("cmd", cmd)
        self.assertEqual(([],), args)
        self.assertEqual({}, kwargs)

    def test_dict(self):
        cmd, args, kwargs = parse("cmd {}")
        self.assertEqual("cmd", cmd)
        self.assertEqual(({},), args)
        self.assertEqual({}, kwargs)

    def test_tuple(self):
        cmd, args, kwargs = parse("cmd ()")
        self.assertEqual("cmd", cmd)
        self.assertEqual(((),), args)
        self.assertEqual({}, kwargs)

    def test_string(self):
        cmd, args, kwargs = parse("cmd ''")
        self.assertEqual("cmd", cmd)
        self.assertEqual(('',), args)
        self.assertEqual({}, kwargs)

        cmd, args, kwargs = parse('cmd ""')
        self.assertEqual("cmd", cmd)
        self.assertEqual(("",), args)
        self.assertEqual({}, kwargs)


class TestParserWithMultipleTokens(unittest.TestCase):
    def test_args(self):
        cmd, args, kwargs = parse("cmd 1 2 3 4 5")
        self.assertEqual("cmd", cmd)
        self.assertEqual((1, 2, 3, 4, 5), args)
        self.assertEqual({}, kwargs)

    def test_kwargs(self):
        cmd, args, kwargs = parse("cmd a=1 b=2 c=3 d=4 e=5")
        self.assertEqual("cmd", cmd)
        self.assertEqual((), args)
        self.assertEqual({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}, kwargs)

    def test_args_and_kwargs(self):
        cmd, args, kwargs = parse("cmd 1 2 3 4 5 a=1 b=2 c=3 d=4 e=5")
        self.assertEqual("cmd", cmd)
        self.assertEqual((1, 2, 3, 4, 5), args)
        self.assertEqual({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}, kwargs)

    def test_recursive_lists(self):
        cmd, args, kwargs = parse("cmd [[] [] [] [] []]")
        self.assertEqual("cmd", cmd)
        self.assertEqual(([[], [], [], [], []],), args)
        self.assertEqual({}, kwargs)

    def test_recursive_dicts(self):
        cmd, args, kwargs = parse("cmd {a:{}, b:{}, c:{}, d:{}, e:{1:56}}")
        self.assertEqual("cmd", cmd)
        self.assertEqual(({"a": {}, "b": {}, "c": {}, "d": {}, "e": {1: 56}},), args)
        self.assertEqual({}, kwargs)

    def test_recursive_tuples(self):
        cmd, args, kwargs = parse("cmd ((), (), (), (), ())")
        self.assertEqual("cmd", cmd)
        self.assertEqual((((), (), (), (), ()),), args)
        self.assertEqual({}, kwargs)


class TestParserExpectedErrors(unittest.TestCase):
    def test_expected_identifier(self):
        with self.assertRaises(SyntaxError):
            parse("1")
            parse("1.0")
            parse("True")
            parse("False")
            parse("None")
            parse("[]")
            parse("{}")
            parse("()")
            parse("''")
            parse('""')
            parse(" ")
            parse("  ")
            parse("   ")
            parse("=")

    def test_kwargs_unexpected(self):
        with self.assertRaises(SyntaxError):
            parse("test a=c d")
            parse("test a=c d=")
            parse("test a=c d=e 1")
            parse("test a=c d=e 1.0")
            parse("test a=c d=e True")
            parse("test a=c d=e False")
            parse("test a=c d=e None")
            parse("test a=c d=e []")
            parse("test a=c d=e {}")
            parse("test a=c d=e ()")
            parse("test a=c d=e ''")
