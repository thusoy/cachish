#!/bin/sh

./venv/bin/py.test --cov cachish --cov-report html:coverage tests/
open coverage/index.html
