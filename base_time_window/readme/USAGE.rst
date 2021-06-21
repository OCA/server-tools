Example implementation for the mixin can be found in module `test_base_time_window`.

As a time window will always be linked to a related model thourgh a M2o relation,
when defining the new model inheriting the mixin, one should pay attention to the
following points in order to have the overlapping check work properly:

- Define class property `_overlap_check_field`: This must state the M2o field to
  use for the to check of overlapping time window records linked to a specific
  record of the related model.

- Add the M2o field to the related model in the `api.constrains`:


For example:

.. code-block:: python

    class PartnerTimeWindow(models.Model):
        _name = 'partner.time.window'
        _inherit = 'time.window.mixin'

        partner_id = fields.Many2one(
            res.partner', required=True, index=True, ondelete='cascade'
        )

        _overlap_check_field = 'partner_id'

        @api.constrains('partner_id')
        def check_window_no_overlaps(self):
            return super().check_window_no_overlaps()
