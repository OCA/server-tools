# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api

from .api import foreach


def _patch_api(cr, registry):
    setattr(api, 'foreach', foreach)
