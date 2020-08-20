# -*- coding: utf-8 -*-
from scake import Scake

class Foo():
    def __init__(self, x):
        self.x = x

    def __call__(self):
        return self.x
    
def test_ref_list_2():
    config = {
        'v0': {
            'v1': {
                'v2': [10, 20, 30],
            }
        },
        'foo': {
            '$Foo': {
                'x': '=/v0/v1/v2',
            }
        },
        'out': {
            '$Foo': {
                'x': [1, '=/foo', 2],
            }
        }
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert isinstance((s['/out'].x)[1], Foo)
    
def test_ref_list_2():
    config = {
        'v0': {
            'v1': {
                'v2': [10, 20, 30],
            }
        },
        'foo': {
            '$Foo': {
                'x': '=/v0/v1/v2',
            }
        },
        'out': [
            '=/foo',
            77,
            88
        ],
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert isinstance(s['/out'][0], Foo)
    
def test_ref_list_1():
    config = {
        'v0': {
            'v1': {
                'v2': [10, 20, 30],
            }
        },
        'foo': {
            '$Foo': {
                'x': '=/v0/v1/v2',
            }
        },
        'out': '=/foo',
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert s['/foo'].x == [10, 20, 30]
    assert s['/out'].x == [10, 20, 30]
    
    
def test_ref_list_obj():
    config = {
        'foo': {
            '$Foo': {
                'x': 10,
            }
        },
        'f0': [1, '=/foo', 3],
        'f1': '=/f0',
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert isinstance(s['/f0'][1], Foo)
    assert isinstance(s['/f1'][1], Foo)
    
def test_ref_list_simple():
    config = {
        'f0': [1, 2, 3],
        'f1': '=/f0',
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert s['/f1'] == [1, 2, 3]
    