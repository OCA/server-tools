# -*- coding: utf-8 -*-
# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ModulePrototyperApiVersion(models.Model):
    _name = 'module_prototyper.api_version'

    name = fields.Char(
        string='Name'
    )
    manifest_file_name = fields.Char(
        string='Manifest File Name'
    )
