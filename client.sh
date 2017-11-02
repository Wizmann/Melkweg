#!/bin/bash

source env/bin/activate

export PYTHONPATH="$PWD/ext/txkcp/src:$PYTHONPATH"
echo $PYTHONPATH

python src/client.py
