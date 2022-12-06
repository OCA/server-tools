The sole purpose of this module is to add an abstract model to be inherited.
So, you will not notice any changes on install.

To develop using this module, you have to inherit the abstract model `conditional.image.consumer.mixin`
to the model that needs the conditional images::

    class ResPartner(models.Model):
        _inherit = ['res.partner', 'conditional.image.consumer.mixin']
        _name = 'res.partner'

Then, configure how the images will be selected for each record.


Note: When migrating from 14.0.1.0.0 to 14.0.2.0.0, please run the 'Resize conditional images'
scheduled actions to regenerate the different sizes of the image.
