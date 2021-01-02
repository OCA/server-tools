Fields that want to implement the language default should use the provided method,such as in the below example::

  class MyModel(models.Model):
      _name = 'my.model'
      time_uom_id = fields.Many2one(
          string='Time Units',
          comodel_name='product.uom',
          default=lambda s: s.env['res.lang'].default_uom_by_category('Time'),
      )
