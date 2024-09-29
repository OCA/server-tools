Store today's date on the company model. A cronjob makes sure this field stays
up-to-date.

The use-case for this module is as follows. Imagine you have two regular fields
and a computed field::

    amount = fields.Monetary()
    payment_date = fields.Date()
    cost_per_day = fields.Monetary(compute="_compute_cost_per_day")

    @api.depends("amount", "payment_date")
    def _compute_cost_per_day(self):
        today = fields.Date.today()
        for record in self:
            delta = today - record.payment_date
            record.cost_per_day = record.amount / delta.days

When the next day arrives, ``cost_per_day`` should be re-computed, but it won't
be, because none of the dependencies have changed.

With this module, you can add a dependency on "company_id.today" (assuming that
your model has a res.company field, which is trivial to add). This way, you get
all the benefits of having a compute cache, and your field will be recomputed
when the date changes.
