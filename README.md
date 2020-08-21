# scake
A flexible framework for Python

<table>
    <tr>
        <td>License</td>
        <td><img src='https://img.shields.io/pypi/l/scake.svg'></td>
        <td>Travis CI</td>
        <td>Master: <img src='https://api.travis-ci.org/kyzas/scake.svg?branch=master'><br/>
        Dev: <img src='https://api.travis-ci.org/kyzas/scake.svg?branch=dev'></td>
    </tr>
    <tr>
        <td>Version</td>
        <td><img src='https://img.shields.io/pypi/v/scake.svg'></td>  
        <td>Coverage</td>
        <td>Master: <img src='https://codecov.io/gh/kyzas/scake/branch/master/graph/badge.svg'><br/>
        Dev: <img src='https://codecov.io/gh/kyzas/scake/branch/dev/graph/badge.svg'></td>
    </tr>
    <tr>
        <td>Wheel</td>
        <td><img src='https://img.shields.io/pypi/wheel/scake.svg'></td>
        <td>Implementation</td>
        <td><img src='https://img.shields.io/pypi/implementation/scake.svg'></td>
    </tr>
    <tr>
        <td>Status</td>
        <td><img src='https://img.shields.io/pypi/status/scake.svg'></td>
        <td>Downloads</td>
        <td><img src='https://img.shields.io/pypi/dm/scake.svg'></td>
    </tr>
    <tr>
        <td>Supported versions</td>
        <td><img src='https://img.shields.io/pypi/pyversions/scake.svg'></td>
    </tr>
</table>

# USAGE

## Hello World with Scake

First, let's define the settings in YAML format.

**settings.yaml**

``` yaml
my_settings:
    hello_message: "Hello World!"

printer:
    $MyPrinter:
        message: =/my_settings/hello_message
    result(): __call__
```

In the above settings, we define the "hello_message" component holding our message: "Hello World!". The reference to it is "=/my_settings/hello_message" (very similar to file path system), first character "=" is annotation for component reference.

At the "printer" component, we initialize an instance of class "MyPrinter" (annotated by $MyPrinter) and pass the message content to its constructor. After initializing instance successfully, Scake will execute the "__call__" function and assign the result to component at "/printer/result()". Open and close parenthesis annotates a method component in Scake.

**hello.py**

``` python
# -*- coding: utf-8 -*-
import sys
import yaml
from scake import Scake

class MyPrinter:
    def __init__(self, message):
        self.message = message

    def __call__(self):
        print(self.message)

def main(yaml_path):
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    s = Scake(config, class_mapping=globals())
    s.run()
    pass

if __name__ == "__main__":
    main(yaml_path="settings.yaml")
```

Run the following command for your first "Hello World!":

``` bash
$ python3 hello.py
Hello World!
```

# FEATURES TO-DO

- [ ] Design logo for Scake.
- [ ] Write documentation & tutorials for Scake.
- [ ] Support "requirements.txt" in settings. Installing Python packages on-the-fly.
- [ ] Support loop in settings.
- [ ] Support flow reference (connect multiple settings files together).
- [ ] Support integration tests (try as friendly as possible).
- [ ] Support generating class templates (> scake /path/to/settings.yaml).
- [ ] Import custom packages automatically by defining in the settings file.
- [ ] Setting element inherit / override.

Far future plan:

- [ ] Packaging scake with Cython.
- [ ] Packaging scake to a library or executable binary.
- [ ] Scake server for listening file changes and update code flow status (ok or error) in real-time.
- [ ] Scake component on the cloud. Be able to reference a scake component by URL @ specific version.
- [ ] Interactive IDE for designing a settings fully compatible to Scake.

# RELEASED FEATURES

## v0.2.3

* Fix bug: initialize object with multiple inheritance

## v0.2.2

* Fix bug: multi-level linking

## v0.2.1

* Object attribute reference in YAML settings
* Fix bug: similar keys in settings

## v0.2.0

* Big refactoring in how we do initializing instances and executing code flow
* Remove generating class templates based on YAML

## v0.1.0

* Automatically initialize Class instances from YAML description.
* Code flow is built and executed properly by checking attribute dependencies.
* Generate class templates based on YAML description.

# CONTRIBUTING

* Step 1. Fork on **dev** branch.
* Step 2. Install **pre-commit** on the local dev environment.

```
pip install pre-commit
pre-commit install
```

* Step 3. Write test case(s) for the new feature or the bug.
* Step 4. Write code to pass the tests.
* Step 5. Make sure that the new code passes all the pre-commmit conditions.

```
pre-commit run -a
```

* Step 6. Create pull request.
