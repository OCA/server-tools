# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    _name = "base.substate.type"
    _description = 'Base Substate Type'
    _order = 'name asc, model asc'

    # Data in this object should be created by import as technical data
    # in specific module ex : sale_subsatate
    name = fields.Char('Substate Name', required=True, translate=True)
    model = fields.Selection(selection=[], string='Apply on', required=True)
    target_state_field = fields.Char(
        required=True, help='Technical target state field name.'
        ' Ex fore sale order "state" for other "status" ... ')


class TargetStateValue(models.Model):
    _name = "target.state.value"
    _description = 'Target State Value'
    _order = 'name asc'

    # Data in this object should be created by import as technical data
    # in specific module ex : sale_subsatate
    name = fields.Char(
        'Target state Name',
        required=True,
        translate=True,
        help='Target state translateble name.'
        ' Ex fore sale order "Quotation", "Sale order", "Locked"...')
    base_substate_type_id = fields.Many2one(
        'base.substate.type',
        string='Substate Type',
        ondelete='restrict',
    )
    target_state_value = fields.Char(
        required=True, help='Technical target state value.'
        ' Ex fore sale order "draft", "sale", "done", ...')
    model = fields.Selection(related='base_substate_type_id.model',
                             store=True, readonly=True,
                             help="Model for technical use")


class BaseSubstate(models.Model):
    _name = "base.substate"
    _description = 'Base Substate'
    _order = 'active desc, sequence asc'

    name = fields.Char('Substate Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(
        index=True,
        help="Gives the sequence order when applying the default substate",
    )
    target_state_value_id = fields.Many2one(
        'target.state.value',
        string='Target State Value',
        ondelete='restrict')
    active = fields.Boolean(default=True)
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'project.task')],
        help="If set, an email will be sent to the partner"
        " when the object reaches this substate.")
    model = fields.Selection(related='target_state_value_id.model',
                             store=True, readonly=True,
                             help="Model for technical use")
