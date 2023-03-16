# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "fetchmail_notify_error_to_sender",
        "migrations/15.0.1.0.1/noupdate_changes.xml",
    )
