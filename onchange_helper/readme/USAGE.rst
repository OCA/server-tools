To use this module, you need to:

* depend on this module
* call `yourmodel.play_onchanges(values, ['field'])`

Example if you want to create a sale order and you want to get the values relative to partner_id field (as if you fill the field from UI)

    `vals = {'partner_id': 1}`

    `vals = self.env['sale.order'].play_onchanges(vals, ['partner_id'])`

Then, `vals` will be updated with partner_invoice_id, partner_shipping_id, pricelist_id, etc...
