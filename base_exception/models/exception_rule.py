# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2020 Hibou Corp.
# Copyright 2023 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models, tools
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

    def _get_rules_info_for_domain(self, domain):
        """returns the rules that match the domain

        This method will call _get_cached_rules_for_domain to get the rules
        that match the domain. This is required to transform the domain
        into a tuple to be used as a key in the cache.
        """
        return self._get_cached_rules_for_domain(tuple(domain))

    @api.model
    @tools.ormcache_context("domain", keys=("lang",))
    def _get_cached_rules_for_domain(self, domain):
        """This method is used to get the rules that match the domain.

        The result is cached to avoid to have to loockup the database every
        time the method is called for rules that never change.

        Recordset are transformed into a dict and then into an object that have
        the same attributes as the exception.rule model. If you need to add
        new attributes to the exception.rule model, you need to add them to
        the dict returned by _to_cache_entry method.
        """
        return [
            type("RuleInfo", (), r._to_cache_entry()) for r in self.search(list(domain))
        ]

    def _to_cache_entry(self):
        """
        This method is used to extract information from the rule to be put
        in cache. It's used by _get_cached_rules_for_domain to avoid to put
        the recordset in cache. The goal is to avoid to have to loockup
        the database to get the information required to apply the rule
        each time the rule is applied.
        """
        self.ensure_one()
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sequence": self.sequence,
            "model": self.model,
            "exception_type": self.exception_type,
            "domain": self._get_domain()
            if self.exception_type == "by_domain"
            else None,
            "method": self.method,
            "code": self.code,
            "is_blocking": self.is_blocking,
        }

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self.env.registry.clear_cache()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res
