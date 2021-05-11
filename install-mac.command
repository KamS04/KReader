#!/bin/bash
cd -- "$(dirname "$BASH_SOURCE")"

if ! command -v python3 > /dev/null
then
    echo Python 3 is not installed
    echo Install Python 3 before running this
    echo Python 3 can be installed from https://www.python.org/downloads/
    exit 127
fi

echo Python 3 exists

if ! command -v python3 -m pip --version > /dev/null
then
    echo Pip is not installed
    echo Download pip from https://bootstrap.pypa.io/get-pip.py
    echo Then run the file with python
fi

echo Pip is installed

if [ ! -d "./venv" ]
then
    echo Creating Virtual Environment
    python3 -m pip install virtualenv
    python3 -m virtualenv venv
else
    echo Virtual Environment Already exists
fi

source ./venv/bin/activate
python3 -m pip install -r dist/requirements.txt
echo installed