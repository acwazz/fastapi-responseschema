## Contributing

Contributions are very welcome!

### How to contribute
Just open an issue or submit a pull request on [GitHub](https://github.com/acwazz/fastapi-responseschema).

While submitting a pull request describe what changes have been made.

## Guidelines
- Try to adhere as much as possible to the Python style and language conventions.
- Add unit tests for classes and methods. 
- When writing features exposed in API, always add documentation following the Google Style Python docstrings.


## Enviroment
This package is developed using Python version `3.8`.

This package uses [poetry](https://python-poetry.org/) to handle dependencies, you can install them with:
```sh
poetry install -E pagination
```


## Formatting
[Black](https://black.readthedocs.io/en/stable/) is used to provide code autoformatting e linting.
Before committing your changes run `black`:
```sh
black .
```

## Type checking
[mypy](https://mypy.readthedocs.io/en/stable/index.html) is used to statically type check the source code.
Before committing your changes run `mypy`:
```sh
mypy fastapi_responseschema
```

## Testing
Tests are written using [pytest](https://docs.pytest.org/en/7.1.x/).
To run the test suite just type in your terminal:
```sh
pytest
```
This will generate the coverage in html format in a root level directory `htmlcov`.


## Documentation
Documentation is built using [pydoc-markdown](https://niklasrosenstein.github.io/pydoc-markdown/).
To run the documentation dev server:
```sh
novella -d docs --serve
```
To build the docs:
```sh
novella -d docs
```
