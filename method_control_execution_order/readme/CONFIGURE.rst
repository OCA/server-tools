For each override you want to order, you will have to create a "method.overload" record::

    <record id="model_overridden_method" model="method.overload">::
        <field name="method_name">overridden_method</field>
        <field name="method_model">model</field>
        <field name="method_delegate_name">delegate_method</field>
        <field name="sequence">1</field>
    </record>

The override logic should be delegated to another method like so::

    def overridden_method(self):::
        res = super().overridden_method()
        return delegate_method(res)

    def delegate_method(self, res):::
        # alter result here
        return res

In order to make it configurable, you'll have to add a Many2many field on the company,
and display it in the related configuration section.
