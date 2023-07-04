# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2020 Hibou Corp.
# Copyright 2023 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ExceptionRule(models.Model):
    _name = "exception.rule"
    _description = "Exception Rule"
    _order = "active desc, sequence asc"

    name = fields.Char("Exception Name", required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(help="Gives the sequence order when applying the test")
    model = fields.Selection(selection=[], string="Apply on", required=True)

    exception_type = fields.Selection(
        selection=[
            ("by_domain", "By domain"),
            ("by_py_code", "By python code"),
            ("by_method", "By method"),
        ],
        required=True,
        default="by_py_code",
        help="By python code: allow to define any arbitrary check\n"
        "By domain: limited to a selection by an odoo domain:\n"
        "           performance can be better when exceptions"
        "           are evaluated with several records\n"
        "By method: allow to select an existing check method",
    )
    domain = fields.Char()
    method = fields.Selection(selection=[], readonly=True)
    active = fields.Boolean(default=True)
    code = fields.Text(
        "Python Code",
        help="Python code executed to check if the exception apply or "
        "not. Use failed = True to block the exception",
    )
    is_blocking = fields.Boolean(
        help="When checked the exception can not be ignored",
    )

    @api.constrains("exception_type", "domain", "code", "model")
    def check_exception_type_consistency(self):
        for rule in self:
            if (
                (rule.exception_type == "by_py_code" and not rule.code)
                or (rule.exception_type == "by_domain" and not rule.domain)
                or (rule.exception_type == "by_method" and not rule.method)
            ):
                raise ValidationError(
                    _(
                        "There is a problem of configuration, python code, "
                        "domain or method is missing to match the exception "
                        "type."
                    )
                )

    def _get_domain(self):
        """override me to customize domains according exceptions cases"""
        self.ensure_one()
        return safe_eval(self.domain)
