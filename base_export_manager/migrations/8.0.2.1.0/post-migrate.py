# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.addons.base_export_manager import post_init_hook


def migrate(cr, version):
    """When updating, now you need the post_init_hook."""
    post_init_hook(cr, None)
