# -*- coding: utf-8 -*-
##############################################################################
#
#    See __openerp__.py about license
#
##############################################################################

from openerp import models, fields


class IrModelFieldsRegex(models.Model):
    _name = "ir.model.fields.regex"
    name = fields.Char('Description', required=True)
    regex = fields.Char(
        'Regular Expression', required=True,
        help="Regular expression used to validate the field. For example, "
             "you can add the expression\n%s\nto the email field"
             % r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b')
