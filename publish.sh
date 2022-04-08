#!/usr/bin/env bash

# tag the release version and confirm a clean version number
git tag vxxxx
git describe --tag --dirty --always 

set -e

rm -rf dist
python setup.py sdist bdist_wheel
twine upload dist/*
