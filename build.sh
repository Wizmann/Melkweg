#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

virtualenv --clear $BASEDIR/env

echo $BASEDIR/env/bin/activate
source $BASEDIR/env/bin/activate

pip install -r $BASEDIR/requirements.txt

mkdir $BASEDIR/ext
cd $BASEDIR/ext
git clone https://github.com/Wizmann/txkcp.git
git clone https://github.com/Wizmann/python-ikcp.git

cd python-ikcp
python setup.py build
python setup.py install
