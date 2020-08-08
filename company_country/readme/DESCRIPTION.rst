**Note:** This module is not required anymore for Odoo >= 13.0, thanks to
`this fix introduced in Odoo <https://github.com/odoo/odoo/pull/52117>`_.

This module allows to set a country to the main company before the ``account``
module is installed, so the hook of that module installs the correct
``l10n_***`` module.

This is useful because, if the company isn't already set correctly when the
``account`` module is installed, the generic accounting chart will be installed
(``l10n_generic_coa``), which may be incorrect depending on your company's
country.
