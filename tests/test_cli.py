# -*- coding: utf-8 -*-
import sys
import os
import shutil
from scake import Scake
import scake.cli as scake_cli

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
YAML_DIR = 'sample_yaml'
COMPLEX_FLOW = 'complex_flow.yaml'


def test_generate_class():
    scake_cli.main(['scake', 'generate', os.path.join(CURRENT_PATH, YAML_DIR, COMPLEX_FLOW)])

    cwd = os.getcwd()
    scake_packages = os.path.join(cwd, Scake.GENERATED_SCAKE_PACKAGES_NAME)
    is_package_dir_exist = os.path.isdir(scake_packages)
    is_init_py_exist = os.path.isfile(os.path.join(scake_packages, '__init__.py'))

    is_scake_modules_exist = []
    scake_modules = [
        'mysum',
        'myprod',
        'mypow',
        'totalsum'
    ]
    for mod_name in scake_modules:
        mod_path = os.path.join(scake_packages, '%s.py' % mod_name)
        is_scake_modules_exist.append(os.path.isfile(mod_path))

    # add scake packages to system path
    sys.path.append(scake_packages)
    is_able_to_import_correctly = True
    try:
        from mysum import MySum_  # check Scake.GENERATED_SCAKE_CLASS_NAME_FORMAT for the pattern!
        from myprod import MyProd_
        from mypow import MyPow_
        from totalsum import TotalSum_
    except Exception as e:
        print('test_generate_class() > Exception: ', str(e))
        is_able_to_import_correctly = False

    is_able_to_init = False
    is_init_correct = False
    if is_able_to_import_correctly:
        try:
            ms = MySum_(a=1, b=2)
            mprod = MyProd_(a=3, b=4)
            mpow = MyPow_(a=5, x=6)
            foo_dict = {'a': 10, 'b': 20}
            ts = TotalSum_(v_dict=foo_dict)
            is_able_to_init = True
            is_init_correct = (ms.a == 1) and (ms.b == 2) and (mprod.a == 3) and (
                mprod.b == 4) and (mpow.a == 5) and (mpow.x == 6) and (ts.v_dict == foo_dict)
        except Exception as e:
            print('test_generate_class() > Exception: ', str(e))
            pass

    # clean
    shutil.rmtree(scake_packages, ignore_errors=True)

    assert is_package_dir_exist
    assert is_init_py_exist
    assert is_scake_modules_exist == [True, True, True, True]
    assert is_able_to_import_correctly
    assert is_able_to_init
    assert is_init_correct
