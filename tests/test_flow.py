# -*- coding: utf-8 -*-
import os
import yaml
from scake import Scake, AutoScake
# from pprint import pprint

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
YAML_DIR = 'sample_yaml'
SIMPLE_FLOW = 'simple_flow.yaml'
FLEXIBLE_FLOW = 'flexible_flow.yaml'
COMPLEX_FLOW = 'complex_flow.yaml'


class MyMain():
    def __init__(self, text):
        self.text = text
        self.out = None

    def __call__(self):
        print(self.text)
        return self.text


class MyAnswer():
    def __init__(self, question):
        self.question = question

    def __call__(self):
        return self.question.lower()


class MySum():
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self):
        return self.a + self.b


class MyProd():
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self):
        return self.a * self.b


class MyPow():
    def __init__(self, a, x):
        self.a = a
        self.x = x

    def __call__(self):
        return pow(self.a, self.x)


class TotalSum():
    def __init__(self, v_dict):
        self.v_dict = v_dict

    def __call__(self):
        return sum(list(self.v_dict.values()))


# set up scake
Scake.app(classes=globals())


def test_calling_with_complex_flow():
    complex_settings = os.path.join(CURRENT_PATH, YAML_DIR, COMPLEX_FLOW)
    auto = AutoScake(complex_settings)
    auto.run()

    assert auto.phase_1.sum_1.out == 3
    assert auto.phase_1.prod_1.out == 15
    assert auto.phase_1.pow_1.out == 225
    assert auto.phase_1.prod_2.out == 45
    assert auto.phase_2.sum.out == 60
    assert auto.phase_2.neg.out == -60
    assert auto.phase_2.sub.out == 165
    assert auto.final_result.out == 453


def test_calling_with_simple_constraint():
    flexible_settings = os.path.join(CURRENT_PATH, YAML_DIR, FLEXIBLE_FLOW)
    auto = AutoScake(flexible_settings)
    auto.run()

    assert auto.entry.out == auto.data.hello
    assert auto.neutral_node.node_out == 'Neutral Node'
    assert auto.next_stage.answer.question == auto.entry.out
    assert auto.next_stage.answer.result == auto.entry.out.lower()


def test_calling():
    yaml_file = os.path.join(CURRENT_PATH, YAML_DIR, SIMPLE_FLOW)
    auto = AutoScake(yaml_file)
    auto.run()
    assert auto.entry.out == auto.data.hello
    assert auto.entry.out == 'Hello Scake!'


def test_yaml_loading():
    yaml_file = os.path.join(CURRENT_PATH, YAML_DIR, SIMPLE_FLOW)
    auto = AutoScake(yaml_file)

    with open(yaml_file) as f:
        data_dict = yaml.safe_load(f)

    assert auto.exec_graph == data_dict
    assert auto.data.hello == 'Hello Scake!'
    assert auto.entry.text == 'Hello Scake!'
