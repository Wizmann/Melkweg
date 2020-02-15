#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"

cd $DIR

source env/bin/activate

export PYTHONPATH="$PWD/ext/txkcp/src:$PYTHONPATH"

python src/client.py
