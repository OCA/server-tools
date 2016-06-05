# -*- coding: utf-8 -*-
# © 2016  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    # Tis method is extracted from odoo/odoo v9.0
    @api.multi
    # pylint: disable=dangerous-default-value
    def _get_module_upstream_dependencies(
            self, mod_ids, known_dep_ids=None,
            exclude_states=['installed', 'uninstallable', 'to remove']):
        """Copied from odoo native ir.module.module v9.0
        Return the dependency tree of modules of the given `ids`, and that
        satisfy the `exclude_states` filter """
        # To Avoid overwrite the origina method
        ids = mod_ids
        cr = self.env.cr
        if not ids:
            return []
        known_dep_ids = set(known_dep_ids or [])
        cr.execute(
            '''SELECT DISTINCT m.id
            FROM
                ir_module_module_dependency d
            JOIN
                ir_module_module m ON (d.module_id=m.id)
            WHERE
                m.name IN (
                    SELECT name
                    from ir_module_module_dependency
                    where module_id in %s) AND
                m.state NOT IN %s AND
                m.id NOT IN %s ''',
            (tuple(ids), tuple(exclude_states), tuple(known_dep_ids or ids)))
        new_dep_ids = set([m[0] for m in cr.fetchall()])
        missing_mod_ids = new_dep_ids - known_dep_ids
        known_dep_ids |= new_dep_ids
        if missing_mod_ids:
            known_dep_ids |= set(
                self._get_module_upstream_dependencies(
                    list(missing_mod_ids), known_dep_ids, exclude_states))
        return list(known_dep_ids)
