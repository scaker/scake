<img src='https://img.shields.io/pypi/l/scake.svg'> <img src='https://img.shields.io/pypi/v/scake.svg'> <img src='https://codecov.io/gh/kyzas/scake/branch/master/graph/badge.svg'> <img src='https://img.shields.io/pypi/dm/scake.svg'> <img src='https://img.shields.io/pypi/pyversions/scake.svg'> <img src='https://img.shields.io/badge/code%20style-black-000000.svg'>

# scake
A flexible framework for Python

# NOTE

Scake version from v0.3.0+ is not compatible to older version (v0.2.4-). Accepted annotation of Scake has the following format:

```
a:
    b: 10
c: /a/b         # 10

instead of this in the older Scake version:

a:
    b: 10
c: =/a/b         # 10
```

# USAGE

Update later

# CONTRIBUTING

* Step 1. Fork on **master** branch.
* Step 2. Install **pre-commit** on the local dev environment.

```
pip install pre-commit
pre-commit install
#pre-commit autoupdate
```

* Step 3. Write test case(s) for the new feature or the bug.
* Step 4. Write code to pass the tests.
* Step 5. Make sure that the new code passes all the pre-commmit conditions.

```
pre-commit run -a
```

* Step 6. Create pull request.
