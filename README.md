# cachish

Cache-ish thingie for serving stale responses when source is unavailable. Useful when you absolutely need to get something from the network before starting something else, but accept getting a stale response if the network or external resource is unavailable.

Also helps with privilege separation, ensuring your main code can run without needing arbitrary network privileges, or needing unrestricted API tokens to external resources.

One use case is running a service outside Heroku, but using a Heroku-hosted database. When you start your service you need to resolve the database's url, since Heroku might change these on a whim, which requires asking the Heroku API for the current URL, but you don't want your app to fail when the Heroku API is unavailable, such as during maintenance. In this case you would configure cachish with a Heroku API token that gains access to the app that hosts your database, and your main app would ask cachish for the database url, instead of asking Heroku directly. This prevents your app from gaining access to other configuration variables the database host app might hold, and enables it to start with the old database url if the Heroku API is unavailable.


Local development
-----------------

    $ ./configure
    $ ./test

To re-run tests whenever you change something, do:

    $ ./tools/watch_and_run_tests.sh
