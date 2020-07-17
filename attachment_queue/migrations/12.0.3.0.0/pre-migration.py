# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.rename_fields(
        env,
        [("attachment.queue", "attachment_queue", "state_message", "error_message")],
    )
