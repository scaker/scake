# -*- coding: utf-8 -*-
from scake import Scake

class Foo():
    def __init__(self, x):
        self.x = x

    def __call__(self):
        return self.x
    
class Bar():
    def __init__(self, y):
        self.y = y
    
def test_ref_obj_complex_1():
    config = {
        'const': {
            'size': 10,
        },
        'transforms': {
            'resize': {
                '$Foo': {
                    'x': '=/const/size', # <= bug risk!!
                }
            }
        },
        'gvnet': {
            'main': '=/aug/compose',
            'train': {
                'cifar10': [
                    '=/transforms/resize',
                ]
            }
        },
        'aug': {
            'compose': {
                '$Bar': {
                    'y': '=/gvnet/train/cifar10',
                }
            }
        },
        'dataset': {
            'train': {
                '$Bar': {
                    'y': '=/gvnet/main',
                }
            }
        },
        'dataloader': {
            'train': {
                '$Bar': {
                    'y': '=/dataset/train',
                }
            }
        },
        'trainer': {
            'cifar': {
                '$Bar': {
                    'y': '=/dataloader/train',
                }
            }
        }
    }

    s = Scake(config, class_mapping=globals())
    s.run(debug=True)

    trainer = s['/trainer/cifar']
    dataloader = trainer.y
    dataset = dataloader.y
    compose = dataset.y
    transform_list = compose.y
    resize = transform_list[0]
    assert isinstance(resize, Foo)
    