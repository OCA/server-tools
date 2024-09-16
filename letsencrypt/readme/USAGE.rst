The module sets up a cronjob that requests and renews certificates automatically.

Certificates are renewed a month before they expire. Renewal is then attempted
every day until it succeeds.

After the first run, you'll find a file called ``domain.crt`` in
``$datadir/letsencrypt``, configure your SSL proxy to use this file as certificate.

In depth configuration
~~~~~~~~~~~~~~~~~~~~~~

If you want to use multiple domains on your CSR then you have to configure them
from Settings -> General Settings. If you use a wildcard in any of those domains
then letsencrypt will return a DNS challenge. In order for that challenge to be
answered you will need to **either** provide a script (as seen in General Settings)
or install a module that provides support for your DNS provider. In that module
you will need to create a function in the letsencrypt model with the name
``_respond_challenge_dns_$DNS_PROVIDER`` where ``$DNS_PROVIDER`` is the name of your
provider and can be any string with length greater than zero, and add the name
of your DNS provider in the settings dns_provider selection field.

In any case if a script path is inserted in the settings page, it will be run
in case you want to update multiple DNS servers.

A reload command can be set in the Settings as well in case you need to reload
your web server. This by default is ``sudo /usr/sbin/service nginx reload``


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
