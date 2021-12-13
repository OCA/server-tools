# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from threading import current_thread

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.modules.registry import Registry

from ..odoo_patch.odoo_patch import OdooPatch


class GenerateWizard(models.TransientModel):
    _name = "upgrade.generate.record.wizard"
    _description = "Upgrade Generate Record Wizard"

    state = fields.Selection([("draft", "Draft"), ("done", "Done")], default="draft")

    def generate(self):
        """Reinitialize all installed modules.
        Equivalent of running the server with '-d <database> --init all'

        The goal of this is to fill the records table.

        TODO: update module list and versions, then update all modules?"""

        # Truncate the records table
        self.env.cr.execute("TRUNCATE upgrade_attribute, upgrade_record;")

        # Check of all the modules are correctly installed
        modules = self.env["ir.module.module"].search(
            [("state", "in", ["to install", "to upgrade"])]
        )
        if modules:
            raise UserError(
                _("Cannot seem to install or upgrade modules %s")
                % (", ".join([module.name for module in modules]))
            )
        # Now reinitialize all installed modules
        self.env["ir.module.module"].search([("state", "=", "installed")]).write(
            {"state": "to install"}
        )
        self.env.cr.commit()  # pylint: disable=invalid-commit

        # Patch the registry on the thread
        thread = current_thread()
        thread._upgrade_registry = {}

        # Regenerate the registry with monkeypatches that log the records
        with OdooPatch():
            Registry.new(self.env.cr.dbname, update_module=True)

        # Free the registry
        delattr(thread, "_upgrade_registry")

        # Set domain property
        self.env.cr.execute(
            """ UPDATE upgrade_record our
            SET domain = iaw.domain
            FROM ir_model_data imd
            JOIN ir_act_window iaw ON imd.res_id = iaw.id
            WHERE our.type = 'xmlid'
                AND imd.model = 'ir.actions.act_window'
                AND our.model = imd.model
                AND our.name = imd.module || '.' || imd.name
            """
        )
        self.env.cache.invalidate(
            [
                (self.env["upgrade.record"]._fields["domain"], None),
            ]
        )

        # Set constraint definition
        self.env.cr.execute(
            """ UPDATE upgrade_record our
            SET definition = btrim(replace(replace(replace(replace(
                imc.definition, chr(9), ' '), chr(10), ' '), '   ', ' '), '  ', ' '))
            FROM ir_model_data imd
            JOIN ir_model_constraint imc ON imd.res_id = imc.id
            WHERE our.type = 'xmlid'
                AND imd.model = 'ir.model.constraint'
                AND our.model = imd.model
                AND our.name = imd.module || '.' || imd.name"""
        )
        self.env.cache.invalidate(
            [
                (self.env["upgrade.record"]._fields["definition"], None),
            ]
        )

        # Set noupdate property from ir_model_data
        self.env.cr.execute(
            """ UPDATE upgrade_record our
            SET noupdate = imd.noupdate
            FROM ir_model_data imd
            WHERE our.type = 'xmlid'
                AND our.model = imd.model
                AND our.name = imd.module || '.' || imd.name
            """
        )
        self.env.cache.invalidate(
            [
                (self.env["upgrade.record"]._fields["noupdate"], None),
            ]
        )

        # Log model records
        self.env.cr.execute(
            """INSERT INTO upgrade_record
            (create_date, module, name, model, type)
            SELECT NOW() AT TIME ZONE 'UTC',
                imd2.module, imd2.module || '.' || imd.name AS name,
                im.model, 'model' AS type
            FROM (
                SELECT min(id) as id, name, res_id
                FROM ir_model_data
                WHERE name LIKE 'model_%' AND model = 'ir.model'
                GROUP BY name, res_id
                ) imd
            JOIN ir_model_data imd2 ON imd2.id = imd.id
            JOIN ir_model im ON imd.res_id = im.id
            ORDER BY imd.name, imd.id""",
        )

        return self.write({"state": "done"})
