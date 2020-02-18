#!/bin/bash

source env/bin/activate

export PYTHONPATH="$PWD/ext/txkcp/src:$PYTHONPATH"

ulimit -n 10240

python src/server.py
