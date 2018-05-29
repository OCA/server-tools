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

