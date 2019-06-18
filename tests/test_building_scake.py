from scake import Scake
from pprint import pprint

def Person():
    def __init__(self, content):
        self.content = content
        pass
    
    def __call__(self):
        self.out = self.content
        
    def say_what(self, content):
        self.say = content

"""
def test_flow():
    config = {
        'settings': {
            'en': 'hello',
            'fr': 'bonjour'
        },
        'french': {
            '_meta': 'obj',
            'Person': {
                'content': '_/settings/fr'
            },
            'out': 'scake.__call__'
        },
        'eng': {
            '_meta': 'obj',
            'Person': {
                'content': '_/settings/en'
            },
            'out': {
                '_meta': 'func',
                'say_what': {
                    'content': '_/settings/en'
                }
            }
        }
    }
    
    s = Scake(config)
    s.run()
    assert isinstance(s['french'], Person)
    assert s['french'].content == 'bonjour'
    assert s['french'].out == 'bonjour'
    assert isinstance(s['eng'], Person)
    assert s['eng'].content == 'hello'
    assert s['eng'].say == 'hello'
"""

def test_attr_depend():
    config = {
        'group': {
            'key1': 10,
            'key2': 20
        },
        'todo': {
            'one': '_/group/key1',
            'two': {
                'value': '_/todo/one'
            }
        }
    }
    
    s = Scake(config)
    assert s['group/key1'] == 10
    assert s['todo/one'] == s['group/key1']
    assert s['todo/two/value'] == 10

def test_attr_only():
    config = {
        'group_1': {
            'attr_1': 1,
            'attr_2': 2
        },
        'group_2': {
            'group_2a': {
                'attr_2a_1': 'x',
                'attr_2a_2': 'y',
            },
            'group_2b': {
                'attr_2b_1': 'z',
                'attr_2b_2': [
                    {
                        'e0': {
                            'k0': 10
                        }
                    },
                    {
                        'e1': [20, 30]
                    }
                ]
            }
        }
    }
    
    s = Scake(config)
    assert s['group_1/attr_1'] == 1
    assert s['group_1/attr_2'] == 2
    assert s['group_1'] == config['group_1']
    assert s['group_2/group_2a/attr_2a_1'] == 'x'
    assert s['group_2/group_2a/attr_2a_2'] == 'y'
    assert s['group_2/group_2b/attr_2b_1'] == 'z'
    assert s['group_2/group_2b/attr_2b_2/0/e0/k0'] == 10
    assert s['group_2/group_2b/attr_2b_2/1/e1/0'] == 20
    assert s['group_2/group_2b/attr_2b_2/1/e1/1'] == 30
    assert s['group_2/group_2a'] == config['group_2']['group_2a']
    assert s['group_2/group_2b'] == config['group_2']['group_2b']
    assert s['group_2'] == config['group_2']
    assert len(s) == 17
    
