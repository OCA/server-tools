# coding: utf-8
# © 2018 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID

MODELS_TO_EXCLUDE = [
    'onchange.rule',
    'report.base.report_irmodulereference',
    'res.font',
    'res.groups',
    'res.request.link',
    'res.users.log',
    'web_editor.converter.test',
    'web.planner',
    'web_tour.tour',
]


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        models = env["ir.model"].search(
            [
                '|', '|', '|', '|', '|',
                ('transient', '=', True),
                ('model', 'in', MODELS_TO_EXCLUDE),
                ('model', 'like', '%.test.%'),
                ('model', 'like', 'base_import.%'),
                ('model', 'like', 'ir.%'),
                ('model', 'like', 'workflow.%'),
            ])
        models.write({'onchange_rule_unavailable': True})
