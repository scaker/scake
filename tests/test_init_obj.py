# -*- coding: utf-8 -*-
from scake import Scake


class Foo():
    def __init__(self, in_value=0, out_value=0):
        self.in_value = in_value
        self.out_value = out_value

    def get_value(self):
        return self.in_value + self.out_value

    def get_params_x2(self):
        return {
            "in_value": self.in_value * 2,
            "out_value": self.out_value * 2,
        }


def test_init_obj_with_dict():
    config = {
        'config': {
            'foo': {
                'in_value': 2,
                'out_value': 3,
            },
        },
        'foo1': {
            '$Foo': '=/config/foo',
            'get_params_x2()': 'get_params_x2',
        },
        'foo2': {
            '$Foo': '=/foo1/get_params_x2()',
        },
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert s['/foo1/get_params_x2()'] == {'in_value': 2*2, 'out_value': 3*2, }
    assert s['/foo2'].get_params_x2() == {'in_value': 2*2*2, 'out_value': 3*2*2, }
