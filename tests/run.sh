#!/bin/sh

export PYTHONPATH="src/"

coverage run --branch --source=$PYTHONPATH -m pytest tests --ignore=tests/integration

coverage report
coverage html
