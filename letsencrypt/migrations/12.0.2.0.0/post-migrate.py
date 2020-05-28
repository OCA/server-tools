# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID


def migrate_altnames(env):
    config = env["ir.config_parameter"]
    existing = config.search([("key", "=like", "letsencrypt.altname.%")])
    if not existing:
        # If letsencrypt.altnames already exists it shouldn't be clobbered
        return
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
        .search(
            [
                ("ir_actions_server_id.model_id.model", "=", "letsencrypt"),
                ("ir_actions_server_id.code", "=", "model.cron()"),
            ]
        )
    )
    if not jobs:
        # ir.cron._try_lock doesn't handle empty recordsets well
        return
    jobs.write({"interval_type": "days", "interval_number": "1"})
    jobs.mapped("ir_actions_server_id").write({"code": "model._cron()"})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_altnames(env)
    migrate_cron(env)
