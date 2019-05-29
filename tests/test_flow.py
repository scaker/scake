# -*- coding: utf-8 -*-
import os
import yaml
from scake import Scake, AutoScake, ScakeDict

YAML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow_test.yaml')

class MyMain():
    def __init__(self, text):
        self.text = text
        self.out = None
        
    def __call__(self):
        print(self.text)
        return self.text
    
# set up scake
Scake.app(classes=globals())

def test_calling():
    auto = AutoScake(YAML_FILE)
    auto.run()
    assert auto.entry.out == auto.data.hello
    assert auto.entry.out == 'Hello Scake!'

def test_yaml_loading():
    auto = AutoScake(YAML_FILE)
    
    with open(YAML_FILE) as f:
        data_dict = yaml.safe_load(f)
    
    assert auto.exec_graph == data_dict
    assert auto.data.hello == 'Hello Scake!'
    assert auto.entry.text == 'Hello Scake!'
    