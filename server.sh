#!/bin/bash

source env/bin/activate

export PYTHONPATH="$PWD/ext/txkcp/src:$PYTHONPATH"

python src/server.py
