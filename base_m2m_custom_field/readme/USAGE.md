Many2manyCustom field is useful when a direct access to the relational
table is needed, for example to be editable in a dedicated tree view.

Let's consider following models:

``` python
class MyModelA(models.Model):

    _name = 'my.model.a'

    my_model_b_ids = fields.Many2manyCustom(
        'my.model.b',
        'my_model_a_b_rel',
        'my_model_a_id',
        'my_model_b_id',
        create_table=False,
    )


class MyModelB(models.Model):

    _name = 'my.model.b'

    my_model_a_ids = fields.Many2manyCustom(
        'my.model.a',
        'my_model_a_b_rel',
        'my_model_b_id',
        'my_model_a_id',
        create_table=False,
    )


class MyModelABRel(models.Model):

    _name = 'my.model.a.b.rel'

    my_model_a_id = fields.Many2one(
        'my.model.a',
        required=True,
        index=True,  # Index is mandatory here
    )
    my_model_b_id = fields.Many2one(
        'my.model.b',
        required=True,
        index=True,  # Index is mandatory here
    )
```

By setting create_table=False on the Many2manyCustom field, and using
the relational table name, as \_name for the relational model, we're
able to define a dedicated tree view for my.model.a.b.rel.

``` xml
<record id="my_model_a_b_rel_list_view" model="ir.ui.view">
    <field name="name">my.model.a.b.rel.list.view</field>
    <field name="model">my.model.a.b.rel</field>
    <field name="arch" type="xml">
        <list editable="top">
            <field name="my_model_a_id" />
            <field name="my_model_b_id" />
        </list>
    </field>
</record>
```
