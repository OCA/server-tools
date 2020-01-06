To use this module, you need to:

* depend on this module
* call `yourmodel.play_onchanges(values, ['field'])`

Example if you want to create a sale order and you want to get the values relative to partner_id field (as if you fill the field from UI)

    `vals = {'partner_id': 1}`

    `vals = self.env['sale.order'].play_onchanges(vals, ['partner_id'])`

Then, `vals` will be updated with partner_invoice_id, partner_shipping_id, pricelist_id, etc...

Default values will be used to process onchange methods, if respective fields are not set in `vals`.
You can get them if you pass fields name in the list of fields.


    `vals = {'partner_id': 1}`

    `vals = self.env['sale.order'].play_onchanges(vals, ['partner_id', 'date_order'])`

`vals` will contain, in addition to the changed values, the default value for `date_order`


You can also use it on existing record for example:

     `vals = {'partner_shipping_id': 1}`

     `vals = sale.play_onchanges(vals, ['partner_shipping_id'])`

Then the onchange will be played with the vals passed and the existing vals of the sale. `vals` will be updated with partner_invoice_id, pricelist_id, etc..

Behind the scene, `play_onchanges` will execute **all the methods** registered for the list of changed fields, so you do not have to call manually each onchange. To avoid performance issue when the method is called on a record, the record will be transformed into a memory record before calling the registered methods to avoid to trigger SQL updates command when values are assigned to the record by the onchange


Notes:

- Order in onchange_fields is very important as onchanges methods will be played in that order.
- If you use memory object in `vals`, be award that onchange method in base model call `self.invalidate_cache()` that reset it.
