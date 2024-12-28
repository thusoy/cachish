# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

1.7.0 - 2024-12-28
------------------

### Changed
- Swap flask-canonical for flask-events since the latter supports modern flask.
- Update dependencies.
- Move CI to GitHub Actions.

### Fixed
- Fix building debs for bookworm.


1.6.0 - 2019-11-28
------------------

### Changed
- The project license has been changed from MIT to the Hippocratic License to deny use that
  infringes on the United Nations Universal Declaration of Human Rights.

### Added
- Endpoints can now run without authorization by specifying `disable_auth: True` in the config.


1.5.1 - 2019-04-19
------------------

### Fixed
- Updated dependencies.


1.5.0 - 2018-11-09
------------------

### Removed
- Support for python 3.3.

### Fixed
- Updated dependencies, among minor bugfixes this also mitigates [CVE-2018-18074](https://nvd.nist.gov/vuln/detail/CVE-2018-18074).


1.4.0 - 2018-05-26
------------------

### Added
- Authorization can now be done with Basic auth in addition to Bearer tokens.

### Fixed
- Builds consistently for both debian jessie and stretch.


1.3.1 - 2017-09-03
------------------

### Fixed
- Replace custom middleware for canonical logging with flask-canonical.


1.3.0 - 2017-05-11
------------------

### Added
- Add Hawk-authorized JSON backend.


1.2.1 - 2017-02-20
------------------

### Fixed
- Bug in debian postinst causing incorrect permissions on log files


1.2.0 - 2017-02-19
------------------

### Added
- A generic JSON backend: JsonHttp. Configure with a url and field (possibly several) to extract.
- Configureable logging with metrics


1.1.1 - 2017-01-19
------------------

### Fixed
- Failed to start if configured with more than one item
- `~/.netrc` files are now ignored to prevent them overriding authentication


1.1.0 - 2017-01-06
------------------

### Changed
- Configuration of auth tokens changed from `<token>: <url>` to `<client_name>: {token: <token>, url: <url>}`


1.0.0 - 2016-01-04
------------------

First release!
