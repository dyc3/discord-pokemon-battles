#!/bin/bash

set -ex

find . -type f -name "*.py" -exec mypy --pretty {} +
