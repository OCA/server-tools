# © 2025 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo import api
from odoo.cli.shell import Shell
from odoo.tools import config


class ModuleAutoUpgrade(Shell):
    """Run auto upgrade"""

    name = "auto_update"

    def run(self, args):
        self.init(args)
        registry = odoo.registry(config["db_name"])
        with registry.cursor() as cr:
            uid = odoo.SUPERUSER_ID
            # Disabling prefetching of fields here because new fields for
            # res.partner and res.users already exist in the python structures
            # but aren't available in the database yet and would cause exception here
            # This is different from invoking a python shell
            ctx = (
                odoo.api.Environment(cr, uid, {})["res.users"]
                .with_context(prefetch_fields=False)
                .context_get()
            )

            env = api.Environment(cr, uid, ctx)
            env["ir.module.module"].upgrade_changed_checksum(
                overwrite_existing_translations=config[
                    "overwrite_existing_translations"
                ],
            )
        return 0
