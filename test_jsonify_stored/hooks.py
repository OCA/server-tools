# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    """The test model depends on model_export, so we need it before model init."""
    env = api.Environment(cr, SUPERUSER_ID, dict())
    export = env.ref("test_jsonify_stored.model_export", raise_if_not_found=False)
    if not export:
        export = env["ir.exports"].create({"name": "Test Model Export"})
        vals_data = {
            "module": "test_jsonify_stored",
            "name": "model_export",
            "model": export._name,
            "res_id": export.id,
        }
        env["ir.model.data"].create(vals_data)
