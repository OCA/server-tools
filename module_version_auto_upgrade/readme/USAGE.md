Update the `version` key in your modules' `__manifest__.py`, then restart Odoo.

**Note** that the module checks for a *change* in version, not necessarily an
*increase* - so, an upgrade would be triggered even if the module version *decreased*.