#!/bin/bash

grep -v -e pydocstyle -e yapf -e pre-commit requirements-dev.txt | xargs pip install
find tests/unit -type d | grep -v __pycache__ | xargs -n 1 python -m unittest discover
