This module does not provide any immediate new interface features.

The check has to be called from another module via the
function `name_fits_sequence()`. The function returns a Boolean.

As example, a function that re-numbers sale orders on confirmation
using this check, to avoid overriding user-edited names:

```python
  def action_confirm(self):
      for order in self:
          if order.state not in ("draft", "sent"):
              continue
          sequence = self.env["ir.sequence"].search(
              [
                  ("code", "=", "sale.quotation"),
                  ("company_id", "in", [order.company_id.id, False]),
              ],
              order="company_id",
              limit=1,
          )
          if sequence and not sequence.name_fits_sequence(order.name):
              continue
          sequence = (
              self.with_company(order.company_id.id)
              .env["ir.sequence"]
              .next_by_code("sale.order")
          )
          order.write({"name": sequence})
      return super().action_confirm()
```
