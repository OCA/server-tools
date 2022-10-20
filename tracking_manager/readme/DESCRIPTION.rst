This module tracks all fields on every model that has a chatter, including one2many and many2many ones. This excludes the computed, readonly, related fields by default.
In addition, line changes of a one2many field are also tracked (e.g. product_uom_qty of an order_line in a sale order).
