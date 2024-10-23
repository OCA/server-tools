To use this module, you need to:

* depend on this module
* Inherit the `ir.sequence` to fill your custom values

Example:

.. code-block:: python

  class IrSequence(models.Model):
      _inherit = "ir.sequence"

      def _get_special_values(self, date=None, date_range=None):
          values = super()._get_special_values(date=date, date_range=date_range)
          company_code = self.env.company.special_code
          values.update({"company_code": company_code or ""})
          return values`

You can also update the documentation (on the bottom of `ir.sequence` form view) to
describe variables that your add and the purpose of them.

Example:

.. code-block:: XML

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>
      <record model="ir.ui.view" id="ir_sequence_form_view">
          <field name="name">ir.sequence.form (in custom_module)</field>
          <field name="model">ir.sequence</field>
          <field name="inherit_id" ref="base.sequence_view"/>
          <field name="priority" eval="90"/>
          <field name="arch" type="xml">
              <xpath expr="//page[1]" position="inside">
                  <group col="3" name="custom_legend">
                      <group string="Company" name="custom_legend_company">
                          <span colspan="2">Specific company code: {company_code}</span>
                      </group>
                  </group>
              </xpath>
          </field>
      </record>
  </odoo>
