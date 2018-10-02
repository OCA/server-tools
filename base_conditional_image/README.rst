.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=======================
Conditional Images Base
=======================

This module extends the functionality of any model to support conditional images
(based on the record attributes) and to manage them either globally or by company.

The main goal behind this module is to avoid storing the same image multiple times.
For example, for every partner, there is a related image (most of the time, it's the default one).
With this module properly set up, it will be stored only one time and you can change it whenever you want for all partners.

**WARNING**: this module cannot be used on the same objects using the module `base_multi_image`.

Installation
============

The sole purpose of this module is to add an abstract model to be inherited.
So, you will not notice any changes on install.

To develop using this module, you have to inherit the abstract model `abstract.conditional.image`
to the model that needs the conditional images::

    class ResPartner(models.Model):
        _inherit = ['res.partner', 'abstract.conditional.image']
        _name = 'res.partner'

Then, configure how the images will be selected for each record.

Usage
=====

Go to *Technical Settings > Settings > Images* to configure all the images.
You can define images for specific objects, depending on the attributes and the company of the object.

The `selector` should return a boolean expression. All fields of the object are available to compute the result.

The system will first try to match an image with a company set up, then with the ones without a company.
If your object does not have a `company_id` field, this check will be ignored and only images without a company will be used.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20custom_image%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Patrick Tombez <patrick.tombez@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
