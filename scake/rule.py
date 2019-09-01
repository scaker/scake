# -*- coding: utf-8 -*-
class Rule():
    path_symbol = '='
    class_symbol = '$'
    separator = '/'
    method_symbol = '()'  # method or def or function

    type_class = 'class'
    type_method = 'def'

    def __init__(self, path_symbol=None, class_symbol=None, separator=None, method_symbol=None):
        self.path_symbol = path_symbol or Rule.path_symbol
        self.class_symbol = class_symbol or Rule.class_symbol
        self.separator = separator or Rule.separator
        self.method_symbol = method_symbol or Rule.method_symbol
        pass

    def check_type(self, key):
        if self.is_class(key):
            return Rule.type_class
        if self.is_method(key):
            return Rule.type_method
        return None

    def is_method(self, key):
        return key.endswith(self.method_symbol) and key.count(self.method_symbol) == 1

    def is_class(self, key):
        last_elem = key.split(self.separator)[-1]
        if last_elem.startswith(self.class_symbol) and last_elem.count(self.class_symbol) == 1:
            return last_elem[1:]
        else:
            return None
        pass

    def is_ref(self, ref, is_remove_attr=False):
        if isinstance(ref, str) and \
                ref.startswith(self.path_symbol) and \
                ref.count(self.separator) > 0:
            if is_remove_attr and ref.split(self.separator)[-1].count('.') > 0:
                new_ref = ref.split(self.separator)
                new_ref[-1] = new_ref[-1].split('.')[0]
                return self.separator.join(new_ref)[1:]
            return ref[1:]
        else:
            return None
        pass
