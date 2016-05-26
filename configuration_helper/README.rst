.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Configuration Helper
====================

*This module is intended for developer only. It does nothing used alone.*

It helps to create `config.settings` by providing an abstract Class.

This class:

  * creates automatically related fields in 'whatiwant.config.settings'
    using those defined in 'res.company': it avoids duplicated field definitions.
  * company_id field with default value is created
  * onchange_company_id is defined to update all related fields
  * supported fields: char, text, integer, float, datetime, date, boolean, m2o


How to use
----------

.. code-block:: python

    from . company import ResCompany

    class WhatiwantClassSettings(orm.TransientModel):
        _inherit = ['res.config.settings', 'abstract.config.settings']
        _name = 'whatiwant.config.settings'
        # fields must be defined in ResCompany class
        # related fields are automatically generated from previous definitions
        _companyObject = ResCompany
        # all prefixed field with _prefix in res.company, will be available in 'whatiwant.config.settings' model
        _prefix = 'prefixyouchoose_'


Roadmap
-------
  * support (or check support) for these field types : o2m, m2m, reference, property, selection
  * automatically generate a default view for 'whatiwant.config.settings' (in --debug ?)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* David BEAL <david.beal@akretion.com>
* Sébastien BEAU <sebastien.beau@akretion.com>
