# -*- coding: utf-8 -*-
import os
import sys
import yaml
from .scake import Scake


def find_class_params(exec_dict, class_names_list):
    class_param_dict = {}

    for key, value in exec_dict.items():
        if key in class_names_list:
            # value is a dict, we extract the keys in this dict
            param_names = list(value.keys())
            # then add to the result dict
            if key not in class_param_dict:
                class_param_dict[key] = param_names
            else:
                class_param_dict[key] += param_names
            pass

        if isinstance(value, dict):
            child_result_dict = find_class_params(value, class_names_list)
            # merge child dict to the current dict
            for ck, cv in child_result_dict.items():
                if ck in class_param_dict:
                    class_param_dict[ck] += child_result_dict[ck]
                else:
                    class_param_dict[ck] = child_result_dict[ck]
                pass
            pass
        pass

    # make list of param names be unique
    for ck, cv in class_param_dict.items():
        class_param_dict[ck] = list(set(cv))

    return class_param_dict


def find_class_names(exec_dict):
    class_names_list = []
    for key, value in exec_dict.items():
        if key[0].isupper():
            class_names_list.append(key)

        if isinstance(value, dict):
            class_names_list += find_class_names(value)
    return list(set(class_names_list))


def load_yaml_as_dict(yaml_path):
    if not os.path.isfile(yaml_path):
        return {}
    data_dict = {}
    with open(yaml_path) as f:
        data_dict = yaml.safe_load(f)
    return data_dict


def create_empty_default_files(parent_dir, default_files):
    for df in default_files:
        df_path = os.path.join(parent_dir, df)
        if not os.path.isfile(df_path):
            open(df_path, 'a').close()
        pass
    pass


def main(argv_list=None):
    argv_list = argv_list if argv_list else sys.argv
    scake_command, exec_yaml = argv_list[1:]

    cwd = os.getcwd()
    scake_packages = os.path.join(cwd, Scake.GENERATED_SCAKE_PACKAGES_NAME)
    if not os.path.isdir(scake_packages):
        os.makedirs(scake_packages)

    default_files = [
        '__init__.py'
    ]

    create_empty_default_files(parent_dir=scake_packages, default_files=default_files)
    exec_dict = load_yaml_as_dict(yaml_path=exec_yaml)

    class_names_list = find_class_names(exec_dict=exec_dict)
    module_names_list = ['%s.py' % cn.lower() for cn in class_names_list]
    create_empty_default_files(parent_dir=scake_packages, default_files=module_names_list)

    # loop one more time to find class params for initialization
    class_param_dict = find_class_params(exec_dict, class_names_list)

    for idx, mod_name in enumerate(module_names_list):
        scake_class_name = Scake.GENERATED_SCAKE_CLASS_NAME_FORMAT % {
            'class_name': class_names_list[idx]
        }
        scake_class_param_list = sorted(class_param_dict[class_names_list[idx]])

        init_params = []
        for param_name in scake_class_param_list:
            init_params.append('%s=None' % param_name)
        init_params = ', '.join(init_params)

        assign_params = []
        for param_name in scake_class_param_list:
            assign_params.append('        self.%s = %s' % (param_name, param_name))  # 8-spaces indentation
        assign_params = '\n'.join(assign_params)

        mod_path = os.path.join(scake_packages, mod_name)
        with open(mod_path, 'w') as f:
            f.write(Scake.GENERATED_SCAKE_CLASS_CODE % {
                'scake_class_name': scake_class_name,
                'init_params': init_params,
                'assign_params': assign_params,
            })
        pass

    # modify __init__.py in scake packages
    init_py_path = os.path.join(scake_packages, '__init__.py')
    init_py_content = []

    for cn in class_names_list:
        py_name = cn.lower()
        class_name = Scake.GENERATED_SCAKE_CLASS_NAME_FORMAT % {'class_name': cn}
        init_py_content.append('from .%s import %s' % (py_name, class_name))

    with open(init_py_path, 'w') as f:
        f.write('\n'.join(init_py_content))

    pass


if __name__ == '__main__':
    main(sys.argv)
