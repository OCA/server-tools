.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Keychain Account
================

This module allows you to store credentials of external systems.

* All the crendentials are stored in one place: easier to manage and to audit.
* Multi-account made possible without effort.
* Store additionnal data for each account. 
* Validation rules for additional data


By default passwords are encrypted with a key stored in odoo config.
It's far from an ideal password storage setup, but it's way better 
than password in clear text in the database.
It can be easily replaced with another system. See "Security" chapter below.

Accounts may be: market places (Amazon, Cdisount, ...), carriers (Laposte, UPS, ...) or any third party system called from odoo.

This module is usefull for developers.
The logic to choose between accounts or environement (like dev or prod) is done in dependant modules.


==========
Uses cases
==========

For delivery, each warehouse send parcels with his own account to the same carrier.


Configuration
=============

After the installation of this module, you need to add an entry in odoo's config file : 
(etc/openerp.cfg) :
> keychain_key = fyeMIx9XVPBBky5XZeLDxVc9dFKy7Uzas3AoyMarHPA=

You can generate keys with `python keychain/bin/generate_key.py`

This key is used to encrypt account passwords.


Usage (for module dev)
======================


* Add this keychain as a dependency in __openerp__.py
* Subclass `keychain.account` and add your module in namespaces : `(see after for the name of namespace )`

.. code:: python

    class LaposteAccount(models.Model):
        _inherit = 'keychain.account'

        namespace = fields.Selection(
            selection_add=[('roulier_laposte', 'Laposte')])

* Add the default data (as dict):

.. code:: python

    class LaposteAccount(models.Model):
        # ...
        def _roulier_laposte_init_data(self):
            return {
                "agencyCode": "",
                "recommandationLevel": "R1"
            }

* Implement validation of user entered data:

.. code:: python

    class LaposteAccount(models.Model):
        # ...
        def _roulier_laposte_validate_data(self, data):
            return len(data.get("agencyCode") > 3)

* In your code, fetch the account :

.. code:: python

    def get_auth(self):
        import random
        accounts = self.env['keychain.account'].search(
            [['namespace', '=', 'roulier_laposte']])
        account = random.choice(accounts)
        return {
            'login': account.login,
            'password': account.get_password()
        }


In this example, an account is randomly picked. Usually this is set according to rules specific for each client.

Warning: _init_data and _validate_data should be prefixed with your namespace !
Choose python naming function compatible name.


Usage (for user)
================

Go to *settings / keychain*, create a record with the following 

* Namespace: type of account (ie: Laposte)
* Name : human readable label "Warehouse 1"
* Technical Name: name used by a consumer module, should be unique for this module (like "wharehouse_1")
* Login: login of the account
* Password_clear : For entering the password in clear text (not stored unecrypted)
* Password : password encrypted, unreadable without the key (in config)
* data: a JSON string for additionnal values (additionnal config for the account, like : `{"agencyCode": "Lyon", "insuranceLevel": "R1"})`



.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================


Security
========
Common sense : Odoo is not a safe place for storing any sensitive data.

By default, passwords are stored encrypted in the db using symetric encryption [Fernet : https://cryptography.io/en/latest/fernet/]. The encryption key is stored in openerp.tools.config.

Threats :

- unauthorized odoo user want to access data: access is rejected by odoo security rules
 - db is stolen : without the key it's currently pretty hard to recover the password
 - odoo is compromised: hacker can do what he wants with odoo : passwords can be easily decrypted

If you want something more secure, don't store any sensitive data in odoo, use an external system as a proxy, you can still use this module for storing all other data related to your accounts.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Akretion

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Raphaël Reverdy <raphael.reverdy@akretion.com>

Funders
-------

The development of this module has been financially supported by:

* Akretion

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
