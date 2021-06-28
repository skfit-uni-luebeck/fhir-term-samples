#!/bin/bash

venv="venv"

if type deactivate &> /dev/null
then
    echo "deactivating virtual environment prior to script"
    deactivate
fi


if command -v python3 &> /dev/null
then
    python="python3"
elif command -v python &> /dev/null
then
    python="python"
else
    echo "python3 or python command could not be found."
    exit 1
fi

echo "Using python [$python]"
if [ -d $venv ]
then 
    echo "virtual environment exists already at [$venv]"
else
    echo "creating virtual environment at [$venv], this may take a while."
    $python -m venv $venv
    echo "created"
fi

. $venv/bin/activate
echo "Activated virtual environment at [$venv]"

echo "Installing requirements from requirements.txt"
$python -m pip install -r requirements.txt --upgrade

echo "Done setting up virtual environment. Use the following command to activate it, if it is not already activated:"
echo source $venv/bin/activate
