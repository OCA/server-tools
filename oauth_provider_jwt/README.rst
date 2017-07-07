.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
OAuth Provider - JWT
====================

This module adds the JSON Web Token support to OAuth2 provider.

Installation
============

To install this module, you need to:

#. Install the pyjwt and cryptography python modules
#. Install the module like any other in Odoo

Configuration
=============

This module adds a new token type in the OAuth client configuration.

Once the *JSON Web Token* type is selected, a new tab appears at the bottom, where you'll have to select an algorithm for the token signature.

For asymetric algorithms, it is possible to put a custom private key, or the module can generate one for you.
The public key is automatically computed from the private one.

Usage
=====

There is no usage change from the base OAuth2 provider module.

The public key can be retrieved by clients using this URL: http://odoo.example.com/oauth2/public_key?client_id=identifier_of_the_oauth_client

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Known issues / Roadmap
======================

* Add support for the client-side JWT request (https://tools.ietf.org/html/rfc7523)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Sylvain Garancher <sylvain.garancher@syleam.fr>
* Dave Lasley <dave@laslabs.com>

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
