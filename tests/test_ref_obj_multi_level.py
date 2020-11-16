# -*- coding: utf-8 -*-
from scake import Scake


class Foo():
    def __init__(self, x):
        self.x = x

    def __call__(self):
        return self.x


class Bar():
    def __init__(self, foo):
        self.foo = foo

    def __call__(self):
        pass


def test_ref_obj_3_level():
    config = {
        'foo': {
            '$Foo': {
                'x': 2,
            }
        },
        'f1': '=/foo',
        'f2': {
            '$Bar': {
                'foo': '=/f1',
            }
        },
        'f3': '=/f2.foo',
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert isinstance(s['/f1'], Foo)
    assert isinstance(s['/f2'], Bar)
    assert isinstance(s['/f2'].foo, Foo)
    assert isinstance(s['/f3'], Foo)


def test_ref_obj_2_level():
    config = {
        'foo': {
            '$Foo': {
                'x': 2,
            }
        },
        'f1': '=/foo',
        'f2': {
            '$Bar': {
                'foo': '=/f1',
            }
        }
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert isinstance(s['/f1'], Foo)
    assert isinstance(s['/f2'], Bar)
    assert isinstance(s['/f2'].foo, Foo)


def test_ref_obj_1_level():
    config = {
        'foo': {
            '$Foo': {
                'x': 2,
            }
        },
        'fptr': '=/foo',
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert isinstance(s['/fptr'], Foo)
