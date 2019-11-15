# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID


def migrate_altnames(env):
    config = env["ir.config_parameter"]
    existing = config.search([("key", "=like", "letsencrypt.altname.%")])
    new_domains = "\n".join(existing.mapped("value"))
    config.set_param("letsencrypt.altnames", new_domains)
    existing.unlink()


def migrate_cron(env):
    # Any interval that was appropriate for the old version is inappropriate
    # for the new one, so it's ok to clobber it.
    # But tweaking it afterwards is fine, so noupdate="1" still makes sense.
    jobs = (
        env["ir.cron"]
        .with_context(active_test=False)
        .search([("model", "=", "letsencrypt"), ("function", "=", "cron")])
    )
    if not jobs:
        # ir.cron._try_lock doesn't handle empty recordsets well
        return
    jobs.write(
        {"function": "_cron", "interval_type": "days", "interval_number": "1"}
    )


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_altnames(env)
    migrate_cron(env)
