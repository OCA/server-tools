.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================================
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

Further, if you force users to https, you'll need something like::

    if ($scheme = "http") {
        set $redirect_https 1;
    }
    if ($request_uri ~ ^/.well-known/acme-challenge/) {
        set $redirect_https 0;
    }
    if ($redirect_https) {
        rewrite ^   https://$server_name$request_uri? permanent;
    }

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20letsencrypt%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

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
