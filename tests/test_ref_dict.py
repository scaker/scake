# -*- coding: utf-8 -*-
from scake import Scake

import logging
_logger = logging.getLogger(__name__)


class Foo():
    def __init__(self, x=1, y=2):
        self.x = x
        self.y = y

    def __call__(self):
        x = self.x() if isinstance(self.x, Foo) else self.x
        y = self.y() if isinstance(self.y, Foo) else self.y
        return x + y


class Bar():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y


def test_ref_dict_multi_level():
    config = {
        "config": {
            "myvar_one": {
                "x": 10,
                "y": 20,
            },
            "myvar_two": {
                "x": 100,
                "y": 200,
            },
        },
        "myvar": {
            "one": {
                "$Foo": "=/config/myvar_one"
            },
            "two": {
                "$Foo": "=/config/myvar_two"
            },
        },
        "mybar": {
            "$Bar": {
                "x": "=/myvar",
                "y": 1,
            },
        },
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    mybar = s['/mybar']
    assert isinstance(mybar, Bar)
    assert mybar.get_y() == 1
    assert "one" in mybar.get_x()
    assert "two" in mybar.get_x()
    _logger.warning(mybar.get_x())
    _logger.warning(s["/myvar/one"])
    _logger.warning(s["/myvar/two"])
    assert isinstance(mybar.get_x()["one"], Foo)
    assert isinstance(mybar.get_x()["two"], Foo)
    assert mybar.get_x()["one"]() == 30
    assert mybar.get_x()["two"]() == 300
