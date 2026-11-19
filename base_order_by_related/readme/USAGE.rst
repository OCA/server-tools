In any model where you have a non-stored related field, you can make it sortable::

    class ResPartner(models.Model):
        _inherit = "res.partner"

        country_name = fields.Char(related="country_id.name")

        # make some non-stored related fields sortable
        _order_by_related = ["country_name"]
