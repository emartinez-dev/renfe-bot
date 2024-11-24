#!/bin/sh

export PYTHONPATH="../src"

coverage run --branch --source=$PYTHONPATH -m pytest

coverage report
coverage html
