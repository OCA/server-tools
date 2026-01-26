# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

# DON'T IMPORT THIS MODULE IN INIT TO AVOID THE CREATION OF THE MODELS
# DEFINED FOR TESTS INTO YOUR ODOO INSTANCE
from odoo import models

from ..fields import Vector


class TestModel(models.Model):
    _name = "vector.model"
    _description = "vector.model Fake Model"

    vector = Vector(dimensions=3, string="Default Vector")
    no_autopad = Vector(dimensions=3, string="Vector not autopadded", autopad=False)
