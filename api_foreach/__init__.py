# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo

from .api import foreach


def _patch_api(*arg, **kwargs):
    odoo.api.foreach = foreach
    odoo.api.__all__.append('foreach')
