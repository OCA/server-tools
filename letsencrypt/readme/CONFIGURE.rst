This addons requests a certificate for the domain named in the configuration
parameter ``web.base.url`` - if this comes back as ``localhost`` or the like,
the module doesn't request anything.

If you want your certificate to contain multiple alternative names, just add
them as configuration parameters ``letsencrypt.altname.N`` with ``N`` starting
from ``0``. The amount of domains that can be added are subject to `rate
limiting <https://community.letsencrypt.org/t/rate-limits-for-lets-encrypt/6769>`_.

Note that all those domains must be publicly reachable on port 80 via HTTP, and
they must have an entry for ``.well-known/acme-challenge`` pointing to your odoo
instance.

In depth configuration
~~~~~~~~~~~~~~~~~~~~~~

This module uses ``openssl`` to generate CSRs suitable to be submitted to
letsencrypt.org. In order to do this, it copies ``/etc/ssl/openssl.cnf`` to a
temporary and adapts it according to its needs (currently, that's just adding a
``[SAN]`` section if necessary). If you want the module to use another configuration
template, set config parameter ``letsencrypt.openssl.cnf``.

After refreshing the certificate, the module attempts to run the content of
``letsencrypt.reload_command``, which is by default ``sudo service nginx reload``.
Change this to match your server's configuration.

You'll also need a matching sudo configuration, like::

    your_odoo_user ALL = NOPASSWD: /usr/sbin/service nginx reload

Further, if you force users to https, you'll need something like for nginx::

    if ($scheme = "http") {
        set $redirect_https 1;
    }
    if ($request_uri ~ ^/.well-known/acme-challenge/) {
        set $redirect_https 0;
    }
    if ($redirect_https) {
        rewrite ^   https://$server_name$request_uri? permanent;
    }

and this for apache::

    RewriteEngine On
    RewriteCond %{HTTPS} !=on
    RewriteCond %{REQUEST_URI} "!^/.well-known/"
    RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R,L]

In case you need to redirect other nginx sites to your Odoo instance, declare
an upstream for your odoo instance and do something like::

    location /.well-known {
        proxy_pass    http://yourodooupstream;
    }

If you're using a multi-database installation (with or without dbfilter option)
where /web/databse/selector returns a list of more than one database, then
you need to add ``letsencrypt`` addon to wide load addons list
(by default, only ``web`` addon), setting ``--load`` option.
For example, ``--load=web,letsencrypt``
