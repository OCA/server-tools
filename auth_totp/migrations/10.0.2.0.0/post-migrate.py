# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from uuid import uuid4
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """Generate cookie keys for all users with MFA enabled and clean up."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    user_model = env['res.users'].with_context(active_test=False)
    mfa_users = user_model.search([('mfa_enabled', '=', True)])

    for mfa_user in mfa_users:
        mfa_user.trusted_device_cookie_key = uuid4()

    # Clean up ir records for device model to prevent warnings
    removed_model = 'res.users.device'
    removed_model_record = env['ir.model'].search([
        ('model', '=', removed_model),
    ])
    removed_model_fields = removed_model_record.field_id

    removed_model_fields._prepare_update()
    env['ir.model.constraint'].search([
        ('model', '=', removed_model_record.id),
    ]).unlink()
    env['ir.model.data'].search([
        ('model', '=', 'ir.model'),
        ('res_id', '=', removed_model_record.id),
    ]).unlink()
    cr.execute(
        'DELETE FROM ir_model WHERE model = %s',
        [removed_model],
    )
