@cat ../../README.md :with slice_lines = "108:"

## Guidelines
- Try to adhere as much as possibleto the Python style and language conventions.
- Add unit tests for classes and methods. 
- When writing features exposed in API, always add documentation following the Google Style Python docstrings.

## Enviroment
This package is developed using Python version `3.8`.

This package uses [poetry](https://python-poetry.org/) to handle dependencies, you can install them with:
```sh
poetry install -E pagination
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
