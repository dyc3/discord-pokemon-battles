#!/bin/bash

find tests/unit -type d | grep -v __pycache__ | xargs -n 1 python -m unittest discover
