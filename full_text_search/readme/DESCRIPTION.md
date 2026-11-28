This module provides a simple way to use full-text search functionality in Odoo models.

It is fully based on [PostgreSQL full-text search](https://www.postgresql.org/docs/current/textsearch.html), and adds a new `Searchable` field that represents the TSVector column in the database that will store the weighted full-text vector. It also adds the `full_text` matching operator : `@@` to odoo domains.

To add this functionality to a model, simply add a `Searchable` field to the model with the fields you want to search on weighted by their importance: `A`, `B`, `C`, `D` with `A` being the most important.

```python
from odoo import fields, models

class YourModel(models.Model):
    _name = 'your.model'

    full_text = fields.Searchable(
        "Full Text",
        fields={
            "name": "A",
            "description": "B",
            "notes": "C",
        },
        dictionary="english",
    )
```

And add the `full_text` field to the model's search view (first position is recommended):
```xml
<odoo>
    <record id="view_your_model_search" model="ir.ui.view">
        <field name="model">your.model</field>
        <field name="inherit_id" ref="base.view_your_model_search" />
        <field name="arch" type="xml">
            <field name="name" position="before">
                <field name="full_text" operator="@@" />
            </field>
        </field>
    </record>
</odoo>
```

You can also use the `full_text` operator in your own code to search for records:

```python
  records = self.env['your.model'].search([('full_text', '@@', 'search query')])
```

The search query uses the PostgreSQL websearch syntax with additional prefix matching:

 - unquoted text will be ANDed (`&`)
 - quoted text will be searched for with followed by operator (`<->`)
 - text around the OR keyword will be ORed (`|`)
 - a dash `-` will be treated as a negation operator (`!`)
 - every term will be treated as a prefix match (`:*`)

The results will be sorted by relevance if no other sort order is specified.

By default, the `full_text` field is computed at database level using a generated field (PostgreSQL 12+).

For more fine grained control, you can also use a compute to generate the `full_text` field value yourself.

The usage is as follows:

```python
from odoo import fields, models

class YourModel(models.Model):
    _name = 'your.model'

    full_text = fields.Searchable(
        "Full Text",
        fields={
            "name": "A",
            "description": "B",
            "notes": "C",
        },
        dictionary="english",
        compute="_compute_full_text",
        store=True,
    )

@api.depends('name', 'description', 'notes')
def _compute_full_text(self):
    for record in self:
        record.full_text = {
          "name": record.name,
          "description": record.description,
          "notes": " ".join(record.relation_ids.mapped('name')),
        }
```
