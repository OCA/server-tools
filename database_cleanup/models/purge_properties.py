# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields
REASON_DUPLICATE = 1
REASON_DEFAULT = 2


class CleanupPurgeLineProperty(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.property'
    _description = 'Purge properties'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.property', 'Purge Wizard', readonly=True)
    property_id = fields.Many2one('ir.property')
    reason = fields.Selection([
        (REASON_DUPLICATE, 'Duplicated property'),
        (REASON_DEFAULT, 'Same value as default'),
    ])

    @api.multi
    def purge(self):
        """Delete properties"""
        self.write({'purged': True})
        return self.mapped('property_id').unlink()


class CleanupPurgeWizardProperty(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.property'
    _description = 'Purge properties'

    @api.model
    def find(self):
        """
        Search property records which are duplicated or the same as the default
        """
        result = []
        default_properties = self.env['ir.property'].search([
            ('res_id', '=', False),
        ])
        handled_field_ids = []
        for prop in default_properties:
            if prop.fields_id.id in handled_field_ids:
                continue
            domain = [
                ('id', '!=', prop.id),
                ('fields_id', '=', prop.fields_id.id),
                # =? explicitly tests for None or False, not falsyness
                ('value_float', '=?', prop.value_float or False),
                ('value_integer', '=?', prop.value_integer or False),
                ('value_text', '=?', prop.value_text or False),
                ('value_binary', '=?', prop.value_binary or False),
                ('value_reference', '=?', prop.value_reference or False),
                ('value_datetime', '=?', prop.value_datetime or False),
            ]
            if prop.company_id:
                domain.append(('company_id', '=', prop.company_id.id))
            else:
                domain.extend([
                    '|',
                    ('company_id', '=', False),
                    (
                        'company_id', 'in', self.env['res.company'].search([
                            (
                                'id', 'not in', default_properties.filtered(
                                    lambda x: x.company_id and
                                    x.fields_id == prop.fields_id
                                ).ids,
                            )
                        ]).ids
                    ),
                ])

            for redundant_property in self.env['ir.property'].search(domain):
                result.append({
                    'name': '%s@%s: %s' % (
                        prop.name, prop.res_id, prop.get_by_record()
                    ),
                    'property_id': redundant_property.id,
                    'reason': REASON_DEFAULT,
                })
            handled_field_ids.append(prop.fields_id.id)
        self.env.cr.execute(
            '''
            with grouped_properties(ids, cnt) as (
                select array_agg(id), count(*)
                from ir_property group by res_id, company_id, fields_id
            )
            select ids from grouped_properties where cnt > 1
            '''
        )
        for ids, in self.env.cr.fetchall():
            # odoo uses the first property found by search
            for prop in self.env['ir.property'].search([
                    ('id', 'in', ids)
            ])[1:]:
                result.append({
                    'name': '%s@%s: %s' % (
                        prop.name, prop.res_id, prop.get_by_record()
                    ),
                    'property_id': prop.id,
                    'reason': REASON_DUPLICATE,
                })

        return result

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.property', 'wizard_id', 'Properties to purge')
