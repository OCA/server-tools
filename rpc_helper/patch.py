# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import odoo
from odoo.exceptions import UserError
from odoo.tools.translate import _


def protected__execute_cr(cr, uid, obj, method, *args, **kw):
    # Same as original func in odoo.service.model.execute_cr
    cr.reset()
    recs = odoo.api.Environment(cr, uid, {}).get(obj)
    if recs is None:
        raise UserError(_("Object %s doesn't exist", obj))
    # custom code starts here
    if not _rpc_allowed(recs, method):
        raise UserError(_("RPC call on %s is not allowed", obj))
    return protected__execute_cr._orig__execute_cr(cr, uid, obj, method, *args, **kw)


def _rpc_allowed(recordset, method):
    config = getattr(recordset, "_disable_rpc", None)
    if config is None:
        config = (
            recordset.env["ir.model"]._get_rpc_config(recordset._name).get("disable")
        )
    if config is None:
        return True
    return "all" not in config and method not in config
