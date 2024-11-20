## Via code

Decorate an Odoo model class like this:

    from odoo.addons.rpc_helper.decorator import disable_rpc

    @disable_rpc()
    class AverageModel(models.Model):
        _inherit = "avg.model"

This will disable ALL calls.

To selectively disable only some methods:

    @disable_rpc("create", "write", "any_method")
    class AverageModel(models.Model):
        _inherit = "avg.model"

## Via ir.model configuration

See "Configuration" section.
