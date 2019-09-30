As the controller receiving status updates is unauthenticated, any internet user
can have your server create monitoring instance records. While this is annoying,
it's quite harmless and basically the same as misuse of the fetchmail module.

For a more substantial annoyance, the attacker would have to guess one of your
client's database uuids, so they functionally are your passwords.

To be sure, consider blocking this controller from unknown origins in your SSL
proxy. In nginx, it would look like this::

    location /dead_mans_switch/alive {
    allow   192.168.1.0/24;
    # add other client's IPs
    deny    all;
    }
