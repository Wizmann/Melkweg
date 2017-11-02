#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

virtualenv --clear $BASEDIR/env

echo $BASEDIR/env/bin/activate
source $BASEDIR/env/bin/activate

pip install -r $BASEDIR/requirements.txt

mkdir $BASEDIR/ext
pushd $BASEDIR/ext
git clone --depth 1 https://github.com/Wizmann/txkcp.git
git clone --depth 1 https://github.com/Wizmann/python-ikcp.git

pushd python-ikcp
python setup.py build
python setup.py install

popd
popd

