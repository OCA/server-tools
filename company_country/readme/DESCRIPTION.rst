This module allows to set a country to the main company before the ``account``
module is installed, so the hook of that module installs the correct
``l10n_***`` module.

This is useful because, if the company isn't already set correctly when the
``account`` module is installed, the generic accounting chart will be installed
(``l10n_generic_coa``), which may be incorrect depending on your company's
country.
