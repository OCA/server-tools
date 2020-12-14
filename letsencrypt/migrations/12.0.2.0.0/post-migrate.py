# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os
import urllib.parse

from odoo import api, SUPERUSER_ID

from odoo.addons.letsencrypt.models.letsencrypt import _get_data_dir


def migrate_altnames(env):
    config = env["ir.config_parameter"]
    existing = config.search(
        [("key", "=like", "letsencrypt.altname.%")], order="key"
    )
    base_url = config.get_param("web.base.url", "http://localhost:8069")
    if existing:
        # If letsencrypt.altnames already exists it shouldn't be clobbered
        domains = existing.mapped("value")
        base_domain = urllib.parse.urlparse(base_url).hostname
        if (
            domains
            and base_domain
            and base_domain != "localhost"
            and base_domain not in domains
        ):
            domains.insert(0, base_domain)
        config.set_param("letsencrypt.altnames", "\n".join(domains))
        existing.unlink()

    old_location = os.path.join(
        # .netloc includes the port, which is not right, but that's what
        # the old version did and we're trying to match it
        _get_data_dir(), urllib.parse.urlparse(base_url).netloc
    )
    new_location = os.path.join(_get_data_dir(), "domain")
    if (
        os.path.isfile(old_location + ".crt")
        and os.path.isfile(old_location + ".key")
        and not os.path.isfile(new_location + ".crt")
        and not os.path.isfile(new_location + ".key")
    ):
        os.rename(old_location + ".crt", new_location + ".crt")
        os.symlink(new_location + ".crt", old_location + ".crt")
        os.rename(old_location + ".key", new_location + ".key")
        os.symlink(new_location + ".key", old_location + ".key")


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
