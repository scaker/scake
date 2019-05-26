# -*- coding: utf-8 -*-
import scake

class FooClass():
    def __init__(self, a, b=10, c=''):
        self.a = a
        self.b = b
        self.c = c

class BarClass():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
# set up scake
scake.setup(classes_dict=globals())

def test_init_dict():
    data = {
        'foo': {
            'bar': 1,
            'xyz': 'zyx'
        }
    }
    
    auto = scake.AutoScake(data)    
    assert isinstance(auto.obj, scake.ScakeDict)
    assert auto.obj == data
    assert auto.exec_graph == data
    assert auto.foo == data['foo']
    assert auto.foo.bar == 1
    assert auto.foo.xyz == 'zyx'

def test_init_class():
    data = {
        'FooClass': {
            'a': 5,
            'c': 'custom'
        }
    }
    
    auto = scake.AutoScake(data)
    assert isinstance(auto.obj, FooClass)
    assert auto.obj.a == 5
    assert auto.obj.c == 'custom'
    assert auto.FooClass == data['FooClass']
    
def test_init_class_param_class():
    data = {
        'FooClass': {
            'a': 5,
            'b': 8,
            'c': {
                'BarClass': {
                    'x': 1,
                    'y': 2,
                    'z': 3
                }
            }
        }
    }
    
    auto = scake.AutoScake(data)
    assert isinstance(auto.obj, FooClass)
    assert isinstance(auto.obj.c, BarClass)
    assert auto.obj.c.x == 1
    assert auto.obj.c.y == 2
    assert auto.obj.c.z == 3
    