``views-migration-v17`` is a odoo server mode module that allows you to automatically migrate the views of a Odoo module versión <= v16 to v17 .

For example::

    <field name="test_field_1" attrs="{'invisible': [('active', '=', True)]}"/>
    <field name="test_field_2" attrs="{'invisible': [('zip', '!=', 123)]}"/>
    <field name="test_field_3" attrs="{'readonly': [('zip', '!=', False)]}"/>

To::

    <field name="test_field_1" invisible="active"/>
    <field name="test_field_2" invisible="zip != 123"/>
    <field name="test_field_3" readonly="zip"/>
