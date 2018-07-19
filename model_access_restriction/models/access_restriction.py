# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models

DOMAIN_IR_MODEL_ID = [
    ('model', 'not in', ['access.restriction', 'base', 'res.groups']),
    # Do not allow to restrict ir.* models
    ('model', 'not ilike', 'ir.%'),
    ('transient', '=', False)
]


class AccessRestriction(models.Model):
    """
    Model used to restrict some CRUD action on a specific model to some groups
    only.
    """
    _name = 'access.restriction'
    _description = "Access restriction by group on models and by CRUD action"

    name = fields.Char(
        required=True,
        help="Name of the rule",
    )
    ir_model_id = fields.Many2one(
        "ir.model",
        "Model",
        help="Model to restrict access (CRUD actions)",
        domain=lambda self: self._domain_ir_model_id(),
        required=True,
    )
    model_name = fields.Char(
        related="ir_model_id.model",
        store=True,
        index=True,
        readonly=True,
    )
    perm_create = fields.Boolean(
        "Create",
        help="Use this rule during a create",
        default=False,
        index=True,
    )
    perm_read = fields.Boolean(
        "Read",
        help="Use this rule during a read",
        default=False,
        index=True,
    )
    perm_write = fields.Boolean(
        "Write",
        help="Use this rule during an update/write",
        default=False,
        index=True,
    )
    perm_unlink = fields.Boolean(
        "Unlink",
        help="Use this rule during an unlink/delete",
        default=False,
        index=True,
    )
    active = fields.Boolean(
        default=True,
        help="Enable or disable the restriction rule",
        index=True,
    )
    res_group_ids = fields.Many2many(
        "res.groups",
        string="Groups allowed",
        help="Only users in these groups are allowed to do "
             "specified CRUD actions",
    )

    @api.model
    def _domain_ir_model_id(self):
        """
        Get a domain (to apply on ir.model) to restrict available models
        used to create access.restriction rules.
        :return: list of tuple (domain)
        """
        return DOMAIN_IR_MODEL_ID
