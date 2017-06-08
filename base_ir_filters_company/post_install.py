# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def set_company_to_null(cr, registry):
    cr.execute("""UPDATE ir_filters SET company_id = null""")
