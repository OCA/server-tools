This module is the client part of ``dead_mans_switch_server``. It is responsible
for sending the server status updates, which in turn takes action if those
updates don't come in time.

It also sends CPU and RAM statistics to the server. This is helpful for
assessing a server's health.
