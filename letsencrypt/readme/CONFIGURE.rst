This addons requests a certificate for the domain named in the configuration
parameter ``web.base.url`` - if this comes back as ``localhost`` or the like,
the module doesn't request anything.

Futher self-explanatory settings are in Settings -> General Settings. There you
can add further domains to the CSR, add a custom script that updates your DNS
and add a script that will be used to reload your web server (if needed).
The number of domains that can be added to a certificate is
`capped at 100 <https://letsencrypt.org/docs/rate-limits/>`_. A wildcard
certificate can be used to avoid that limit.

Note that all those domains must be publicly reachable on port 80 via HTTP, and
they must have an entry for ``.well-known/acme-challenge`` pointing to
``$datadir/letsencrypt/acme-challenge`` of your odoo instance.

Since DNS changes can take some time to propagate, when we respond to a DNS challenge
and the server tries to check our response, it might fail (and probably will).
The solution to this is documented in https://tools.ietf.org/html/rfc8555#section-8.2
and basically is a ``Retry-After`` header under which we can instruct the server to
retry the challenge.
At the time these lines were written, Boulder had not implemented this functionality.
This prompted us to use ``letsencrypt.backoff`` configuration parameter, which is the
amount of minutes this module will try poll the server to retry validating the answer
to our challenge, specifically it is the ``deadline`` parameter of ``poll_and_finalize``.
