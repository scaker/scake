# -*- coding: utf-8 -*-

import scake
import pytest

class FooClass():
    def __init__(self, a, b=10, c=''):
        self.a = a
        self.b = b
        self.c = c
        pass

data_dict = {
    'class': 'FooClass',
    'FooClass': {
        'init': {
            'a': 3,
            'b': 2,
            'c': 'foo'
        }
    }
}

# set up scake
scake.setup(globals())

def test_init_instance_from_dict_full_params():
    test_dict = data_dict.copy()
    foo = scake.AutoInit(data_dict=test_dict).get()
    assert foo.a == 3
    assert foo.b == 2
    assert foo.c == 'foo'
    assert isinstance(foo, FooClass)
    
def test_init_instance_from_dict_missing_default_params():
    test_dict = data_dict.copy()
    test_dict['FooClass']['init'] = {
        'a': 1,
        'b': 5
    }
    foo = scake.AutoInit(data_dict=test_dict).get()
    assert foo.a == 1
    assert foo.b == 5
    assert foo.c == ''
    assert isinstance(foo, FooClass)

def test_init_instance_from_dict_missing_required_param():
    test_dict = data_dict.copy()
    test_dict['FooClass'].pop('init')    
    foo = scake.AutoInit(data_dict=test_dict).get()
    assert foo is None

def test_init_instance_from_dict_redundant_params():
    test_dict = data_dict.copy()
    test_dict['FooClass']['init'] = {
        'a': 3,
        'b': 2,
        'c': 'foo',
        'd': '+'
    }
    foo = scake.AutoInit(data_dict=test_dict).get()
    assert foo.a == 3
    assert foo.b == 2
    assert foo.c == 'foo'
    assert foo.d == '+'
    assert isinstance(foo, FooClass)
