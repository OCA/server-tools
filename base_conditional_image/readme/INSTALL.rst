The sole purpose of this module is to add an abstract model to be inherited.
So, you will not notice any changes on install.

To develop using this module, you have to inherit the abstract model `abstract.conditional.image`
to the model that needs the conditional images::

    class ResPartner(models.Model):
        _inherit = ['res.partner', 'abstract.conditional.image']
        _name = 'res.partner'

Then, configure how the images will be selected for each record.
