#!/bin/bash

set -eu

export DH_VIRTUALENV_INSTALL_ROOT=/opt/venvs

main () {
    create_changelog
    dpkg-buildpackage -us -uc
    mkdir -p dist
    mv ../cachish_*{.changes,.deb,.dsc,.tar.gz} dist
}

create_changelog () {
    local author author_email
    author=$(git config user.name)
    author_email=$(git config user.email)
    ./tools/changelog_to_deb.py CHANGELOG.md cachish "$author" "$author_email" \
        > debian/changelog
}

main
