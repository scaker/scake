# -*- coding: utf-8 -*-
from scake import Scake


class Foo():
    def __init__(self, in_value, out_value):
        self.in_value = in_value
        self.out_value = out_value

    def __call__(self):
        return self.in_value + self.out_value


def test_ref_obj_attr():
    config = {
        'foo_obj': {
            '$Foo': {
                'in_value': 2,
                'out_value': 3,
            }
        },
        'fout_obj': {
            '$Foo': {
                'in_value': '=/foo_obj.out_value',
                'out_value': 0,
            },
            'out()': '__call__'
        }
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    assert s['/fout_obj/out()'] == 3
