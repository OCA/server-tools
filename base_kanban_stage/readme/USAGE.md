- Inherit from `base.kanban.abstract` to add Kanban stage functionality to
  the child model:

``` python
class MyModel(models.Model):
    _name = "my.model"
    _inherit = "base.kanban.abstract"
```

- Extend the provided base Kanban view
  (`base_kanban_abstract_view_kanban`) as needed by the child model while
  making sure to set the `mode` to `primary` so that inheritance works
  properly. The base view has four `name` attributes intended to provide
  convenient XPath access to different parts of the Kanban card. They are
  `card_dropdown_menu`, `card_header`, `card_body` and `card_footer`:

``` xml
<record id="my_model_view_kanban" model="ir.ui.view">
    <field name="name">My Model - Kanban View</field>
    <field name="model">my.model</field>
    <field name="mode">primary</field>
    <field name="inherit_id" ref="base_kanban_stage.base_kanban_abstract_view_kanban"/>
    <field name="arch" type="xml">
        <xpath expr="//div[@name='card_header']">
            <!-- Add header content here -->
        </xpath>
        <xpath expr="//main[@name='card_body']">
            <!-- Add body content here -->
        </xpath>
    </field>
</record>
```

- To manage stages, go to Settings \> Technical \> Kanban \> Stages.
