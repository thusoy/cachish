#!/bin/sh

set -eu

main () {
    clean
    build_project
    upload_to_pypi
}

clean () {
    rm -rf dist
}

build_project () {
    ./venv/bin/python setup.py sdist bdist_wheel
}

upload_to_pypi () {
    ./venv/bin/twine upload dist/*
}

main
