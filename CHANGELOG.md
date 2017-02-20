# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/).


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
