# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID


def migrate_altnames(env):
    ir_config_parameter = env['ir.config_parameter']
    new_domains = ','.join(ir_config_parameter.search([
        ('key', '=like', 'letsencrypt.altname.%')]).mapped('value'))
    ir_config_parameter.set_param('letsencrypt_altnames', new_domains)
    ir_config_parameter.search([
        ('key', '=like', 'letsencrypt.altname.%')]).unlink()


def migrate_cron(env):
    ir_cron = env['ir.cron']
    old_cron = ir_cron.search([
        ('model', '=', 'letsencrypt'),
        ('function', '=', 'cron')])
    if old_cron:
        old_cron.write({'function': '_cron'})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_altnames(env)
    migrate_cron(env)
