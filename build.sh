#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

virtualenv --clear $BASEDIR/env

echo $BASEDIR/env/bin/activate
source $BASEDIR/env/bin/activate

pip install -r $BASEDIR/requirements.txt
