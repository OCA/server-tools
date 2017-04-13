.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=======================
Red October Attachments
=======================

This module provides a ``red_october`` type to ``ir.attachment``, which provides
encryption and decryption services using a remote Red October instance.

It also provides some fields & form widgets to allow for similar operation to
internal fields with seamless encryption:

* `.fields.RedOctoberChar` - Acts like `odoo.fields.Char`

Developer Implementation
========================

While this module does technically provide the ability to create standalone encrypted
files, that is not feasible from a usability perspective.

Instead, the preferred approach to allowing encryption is to use the provided fields
in a model and subsequently add into the view.

`Model Example:`
.. code-block:: python

    from odoo.addons.red_october.fields import RedOctoberChar

    class MyModel(odoo.models):
        _name = 'my.model'
        encrypted_field = RedOctoberChar()

`View Example:`
.. code-block:: xml

    <record id="my_model_view_form" model="ir.ui.view">
        <field name="name">My Model Form View</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form string="My Model">
                <field name="encrypted_field" />
            </tree>
        </field>
    </record>

Installation
============

* A working Red October installation is required to use this module, which can easily be
  launched using Docker: ``docker run laslabs/alpine-red-october``
* Install the Python Red October library ``pip install git+https://github.com/LasLabs/python-red-october``

Usage
=====

Create the Vault
----------------

* Go to `Settings => Crypto => Vaults` to create a new vault.
* Once created, a vault must be initialized with an administrative user using the
  `Action => Init Vault` button from the vault form view.
  * If the vault was already activated externally, make sure to check the
    `Already Active` box.

Crypto Profiles
---------------

Crypto Profiles are currently 1:1 with Odoo Users. If a user does not have a Crypto
Profile, it will be created on demand using the Odoo password as the initial password.

Crypto Menu
-----------

The Crypto Menu can be accessed in the top navigation bar by using the dropdown
menu with a lock icon.

The following actions are available in the Crypto Menu:
* Change Profile Password
* Delegate Decryption Rights

Encryption/Decryption
---------------------

* Navigate to a form view implementing an encrypted field
  * When in demo mode, a sample encrypted field is available under the `Preferences`
    tab in the `res.users` form view

If there is a value saved in the encrypted field, the user will be immediately prompted
for their decryption password.

If there is no value in the field, the user is not prompted for a password until they
edit the record, add a value, then save the record.

Once a password is entered, it will be used to decrypt all encrypted fields until the
user refreshes their browser.

The user that initially adds the encrypted value will be the owner of the file. They will
need to subsequently grant ownership others if they also need access to the data.

Note that there must be a valid rights delegation on the Vault in order to decrypt a file,
even if you are the only owner.

Delegate Decryption Rights
--------------------------

Proper rights delegation is required to allow the Red October Vault to decrypt data using
your credentials.

Once decryption rights have expired, a Vault will no longer be able to decrypt your data,
even with the correct password. Adding decryption rights to the Vault again will restore
its ability to decrypt your data.

Note that a Vault can only maintain one delegation at a time per user, so any new delegations
will replace existing delegations for the same user.

* Click the `Crypto Menu`
* Click the name of the Vault you want to delegate rights to
* Enter the delegation information:
  * Number of Uses - How many decryptions are allowed for this delegation
  * Date of Expiration - When will this delegation expire, if the Number of Uses has not been
    exceeded
  * Password - Password to the currently active Crypto Profile

Change Password
---------------

New Crypto Profiles are created using the current user's Odoo password, which is stored as
plain text in the Odoo request session. This is insecure, and it is recommended that all
users immediately change their password before working with sensitive data.

* Click the `Crypto Menu`
* Click `Change Password`
* Enter the requested information

Try It
------

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0 for server-tools

Known issues / Roadmap
======================

* Add caching for most methods
* Allow transferring files between vaults.
* Add delegation uses & delta to ``red.october.file.owner``.
* Proper handling for multiple profiles per user
* All model methods that touch the password or decrypted data need to be moved from
  Odoo models into standard objects. This will provide more security, because the Odoo
  model inheritance magic can be utilized to inject malicious code with a module. Using
  the standard Python inheritance will require that malicious code is placed directly in
  the base module in order to be used.
* Audit Javascript XSS vulnerabilities
* Company rules for automatic ownership of files
* Company rules to enforce password change on Crypto Profiles (initial, and recurrent)
* Company rules to enforce password complexity requirements (glue with
  `OCA/server-tools/password_security`?)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

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

To contribute to this module, please visit http://odoo-community.org.
