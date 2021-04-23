# Copyright 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ModulePrototyperApiVersion(models.Model):
    _name = "module_prototyper.api_version"
    _description = "Module Prototype Api version"

    name = fields.Char()
    manifest_file_name = fields.Char()
