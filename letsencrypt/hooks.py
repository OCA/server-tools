# Copyright 2016-2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, pool):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["letsencrypt"]._get_key("account.key")
