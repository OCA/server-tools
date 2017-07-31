.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Request SSL certificates from letsencrypt.org
=============================================

This module was written to have your Odoo installation request SSL certificates
from https://letsencrypt.org automatically.

Installation
============

After installation, this module generates a private key for your account at
letsencrypt.org automatically in ``$data_dir/letsencrypt/account.key``. If you
want or need to use your own account key, replace the file.

For certificate requests to work, your site needs to be accessible via plain
HTTP, see below for configuration examples in case you force your clients to
the SSL version.

After installation, trigger the cronjob `Update letsencrypt certificates` and
watch your log for messages.

This addon depends on the ``openssl`` binary and the ``acme_tiny`` and ``IPy``
python modules.

For installing the OpenSSL binary you can use your distro package manager.
For Debian and Ubuntu, that would be:

    sudo apt-get install openssl

For installing the ACME-Tiny python module, use the PIP package manager:

    sudo pip install acme-tiny

For installing the IPy python module, use the PIP package manager:

    sudo pip install IPy


Configuration
=============

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

Usage
=====

The module sets up a cronjob that requests and renews certificates automatically.

After the first run, you'll find a file called ``domain.crt`` in
``$datadir/letsencrypt``, configure your SSL proxy to use this file as certificate.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

In depth configuration
======================

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

Further, if you would like users to be automatically redirected to https, you'll need something like for nginx::

    if ($scheme = "http") {
        set $redirect_https 1;
    }
    if ($request_uri ~ ^/.well-known/acme-challenge/) {
        set $redirect_https 0;
    }
    if ($redirect_https) {
        rewrite ^   https://$server_name$request_uri? permanent;
    }

A complete configuration file could look like this::

    upstream odoo {
            server 127.0.0.1:8069;
    }
    upstream odoochat {
            server 127.0.0.1:8072;
    }
    server {
            listen 443;
            listen 80;
            if ($scheme = "http") {
                    set $redirect_https 1;
            }
            if ($request_uri ~ ^/.well-known/acme-challenge/) {
                    set $redirect_https 0;
            }
            if ($request_uri ~ ^/pos/web/) {
                    set $redirect_https 0;
            }
            if ($redirect_https) {
                    rewrite ^   https://$server_name$request_uri? permanent;
            }
            server_name domain.tld www.domain.tld;
            proxy_read_timeout 720s;
            proxy_connect_timeout 720s;
            proxy_send_timeout 720s;

            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Real-IP $remote_addr;

            ssl on;
            ssl_certificate /var/lib/odoo/.local/share/Odoo/letsencrypt/domain.tld.crt;
            ssl_certificate_key /var/lib/odoo/.local/share/Odoo/letsencrypt/domain.tld.key;
            ssl_session_timeout 30m;
            ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
            ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
            ssl_prefer_server_ciphers on;

            access_log /var/log/nginx/odoo.access.log;
            error_log /var/log/nginx/odoo.error.log;        

            location / {
                    proxy_redirect off;
                    proxy_pass  http://odoo;
            }

            location /longpolling {
                    proxy_pass http://odoochat;
            }
            gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript;
            gzip on;
    }

The above configuration file can be put into fx. ``/etc/nginx/sites-enabled/default``

and this for apache::

    RewriteEngine On
    RewriteCond %{HTTPS} !=on
    RewriteCond %{REQUEST_URI} "!^/.well-known/"
    RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R,L]

If you're using a multi-database installation (with or without dbfilter option)
where /web/databse/selector returns a list of more than one database, then
you need to add ``letsencrypt`` addon to wide load addons list
(by default, only ``web`` addon), setting ``--load`` option.
For example, ``--load=web,letsencrypt``


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20letsencrypt%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Antonio Espinosa <antonio.espinosa@tecnativa.com>
* Dave Lasley <dave@laslabs.com>
* Ronald Portier <ronald@therp.nl>

ACME implementation
-------------------

* https://github.com/diafygi/acme-tiny/blob/master/acme_tiny.py

Icon
----

* https://helloworld.letsencrypt.org

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
