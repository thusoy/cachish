#!/bin/sh

set -eu

if [ $# -ne 1 ]; then
    echo "Usage: ./tools/release <version-number>"
    echo
    echo "The version will be updated in setup.py, built and uploaded to PyPI"
    exit 1
fi

version=$1

main () {
    clean
    sanity_check
    bump_version
    patch_changelog
    git_commit
    build_project
    upload_to_pypi
    git_push
}

clean () {
    rm -rf dist
}

sanity_check () {
    # Ensure there are unreleased changes in the changelog
    grep --quiet 'UNRELEASED -' CHANGELOG.md \
        || (
            echo "There's no UNRELEASED section in the changelog, thus nothing to release."
            exit 1
           )
}

bump_version () {
    temp_setup=$(mktemp)
    sed "s/version=.*,/version='$version',/" \
        < setup.py \
        > "$temp_setup"
    mv "$temp_setup" setup.py
}

patch_changelog () {
    release_date=$(date --utc +"%Y-%m-%d")
    temp_changelog=$(mktemp)
    sed "s/UNRELEASED -[ ]*/$version - $release_date/" \
        < CHANGELOG.md \
        > "$temp_changelog"
    mv "$temp_changelog" CHANGELOG.md
}


git_commit () {
    git add setup.py CHANGELOG.md
    git commit --message "Release v$version"
    git tag -m "Release v$version" "v$version"
}

build_project () {
    ./venv/bin/python setup.py sdist bdist_wheel
}

upload_to_pypi () {
    ./tools/upload_pypi.sh
}

git_push () {
    git push --tags
}

main
