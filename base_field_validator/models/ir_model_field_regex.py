# -*- coding: utf-8 -*-
# Copyright © 2014-2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class IrModelFieldsRegex(models.Model):
    _name = "ir.model.fields.regex"
    name = fields.Char('Description', required=True)
    regex = fields.Char(
        'Regular Expression', required=True,
        help="Regular expression used to validate the field. For example, "
             "you can add the expression\n%s\nto the email field"
             % r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b')
