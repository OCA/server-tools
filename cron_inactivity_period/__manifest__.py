# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Inactivity Periods for Cron Jobs",
    "version": "12.0.1.0.1",
    "author": "GRAP,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Tools",
    "depends": ["base"],
    "data": ["security/ir.model.access.csv", "views/ir_cron.xml"],
    "demo": ["demo/res_groups.xml"],
    "images": ["static/description/ir_cron_form.png"],
    "installable": True,
}
