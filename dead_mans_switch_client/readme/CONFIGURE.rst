After installing this module, you need to fill in the system parameter
``dead_mans_switch_client.url``. This must be the full URL to the server's
controller, usually of the form ``https://your.server/dead_mans_switch/alive``.

You can have the number of currently online users logged, but this only
works if the ``bus`` module is installed and longpolling configured correctly.
