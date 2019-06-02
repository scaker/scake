# scake
A flexible framework for Python

<table>
    <tr>
        <td>License</td>
        <td><img src='https://img.shields.io/pypi/l/scake.svg'></td>
        <td>Travis CI</td>
        <td>Master: <img src='https://api.travis-ci.org/kyzas/scake.svg?branch=master'><br/>
        Staging: <img src='https://api.travis-ci.org/kyzas/scake.svg?branch=staging'></td>
    </tr>
    <tr>
        <td>Version</td>
        <td><img src='https://img.shields.io/pypi/v/scake.svg'></td>  
        <td>Coverage</td>
        <td>Master: <img src='https://codecov.io/gh/kyzas/scake/branch/master/graph/badge.svg'><br/>
        Staging: <img src='https://codecov.io/gh/kyzas/scake/branch/staging/graph/badge.svg'></td>
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

# RELEASED FEATURES

## v0.1.0

* Automatically initialize Class instances from YAML description.
* Code flow is built and executed properly by checking attribute dependencies.
* Generate class templates based on YAML description.

# CONTRIBUTING

Step 1. Fork on **staging** branch.
Step 2. Install **pre-commit** on the local dev environment.

```
pip install pre-commit
pre-commit install
```

Step 3. Write test case(s) for the new feature or the bug.
Step 4. Write code to pass the tests.
Step 5. Make sure that the new code passes all the pre-commmit conditions.

```
pre-commit run -a
```

Step 6. Create pull request.
