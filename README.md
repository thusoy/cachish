# cachish [![Build Status](https://github.com/thusoy/cachish/workflows/Tests/badge.svg?branch=main)](https://github.com/thusoy/cachish/actions)

*Ceci n'est pas une cache*

Cache-ish thingie for serving stale responses when source is unavailable. Useful when you absolutely need to get something from the network before starting something else, but accept getting a stale response if the network or external resource is unavailable.

Also helps with privilege separation, ensuring your main code can run without needing arbitrary network privileges, or needing unrestricted API tokens to external resources.

One use case is running a service outside Heroku, but using a Heroku-hosted database. When you start your service you need to resolve the database's url, since Heroku might change these on a whim, which requires asking the Heroku API for the current URL, but you don't want your app to fail when the Heroku API is unavailable, such as during maintenance. In this case you would configure cachish with a Heroku API token that gains access to the app that hosts your database, and your main app would ask cachish for the database url, instead of asking Heroku directly. This prevents your app from gaining access to other configuration variables the database host app might hold, and enables it to start with the old database url if the Heroku API is unavailable.


Local development
-----------------

    $ ./configure
    $ ./test

To re-run tests whenever you change something, do:

    $ ./tools/watch_and_run_tests.sh


Deployment
----------

In decreasing order of stuff you have to do:

* Use the salt state [here](https://github.com/thusoy/salt-states/salt/cachish)
  and configure through pillar. If you're using a different automation tool and
  have written a cookbook/playbook/module/thing for cachish, please let me know
  and I'll add a link to it here!

* Install from my apt repo:
  ```
  $ echo 'deb https://repo.thusoy.com/apt/debian stretch main' | sudo tee -a /etc/apt/sources.list
  $ curl https://raw.githubusercontent.com/thusoy/repo/main/release-key.asc | sudo apt-key add -
  $ sudo apt-get update
  $ sudo apt-get install cachish
  ```
  Configure by editing `/etc/cachish.yml` and restarting the service.

* Build the debian package yourself and upload to your own repo:
  `./tools/build_dep.sh`
* Install from PyPI and run with gunicorn: `pip install cachish[gunicorn]`,
  then `CACHISH_CONFIG_FILE=/path/to/config gunicorn --worker-class gevent 'cachish:create_app_from_file()'`
  (mostly useul for playing around and testing). To deploy on a server you
  should ensure the service is started on boot, drops privileges and has a cache
  directory no other user can read from.
* Clone the repo, install the dependencies (`./configure`), and run
  with `./devserver.py`. Also mostly useful for testing.


License
-------

This project uses the [Hippocratic License](https://firstdonoharm.dev/), and is thus freely
available to use for purposes that do not infringe on the United Nations Universal Declaration of
Human Rights.
