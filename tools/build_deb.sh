#!/bin/bash

set -eu

main () {
    dpkg-buildpackage -us -uc
    mkdir -p dist
    mv ../cachish_*{.changes,.deb,.dsc,.tar.gz} dist
}

main
