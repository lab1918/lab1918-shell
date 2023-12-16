# lab1918-shell
lab1918 shell


## Setup

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Alway format the code before push

```
$ .venv/bin/black .
```

## Test

Run test

```
pip install -r requirements-dev.txt
pip install -e .
pytest or tox
```