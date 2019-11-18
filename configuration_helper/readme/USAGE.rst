.. code-block:: python

    from . company import ResCompany

    class WhatiwantConfigSettings(models.TransientModel):
        _inherit = ['res.config.settings', 'abstract.config.settings']
        _name = 'res.config.settings'
        # fields must be defined in ResCompany class
        # related fields are automatically generated from previous definitions
        _companyObject = ResCompany
        # all prefixed field with _prefix in res.company, will be available in 'res.config.settings' model
        _prefix = 'prefixyouchoose_'

