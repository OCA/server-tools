# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from odoo.tools.cache import ormcache


class ChangesetFieldRule(models.Model):
    _name = "changeset.field.rule"
    _description = "Changeset Field Rules"
    _rec_name = "field_id"

    model_id = fields.Many2one(related="field_id.model_id", store=True)
    field_id = fields.Many2one(
        comodel_name="ir.model.fields", ondelete="cascade", required=True
    )
    action = fields.Selection(
        selection="_selection_action",
        required=True,
        help="Auto: always apply a change.\n"
        "Validate: manually applied by an administrator.\n"
        "Never: change never applied.",
    )
    source_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Source Model",
        ondelete="cascade",
        domain=lambda self: [("id", "in", self._domain_source_models().ids)],
        help="If a source model is defined, the rule will be applied only "
        "when the change is made from this origin.  "
        "Rules without source model are global and applies to all "
        "backends.\n"
        "Rules with a source model have precedence over global rules, "
        "but if a field has no rule with a source model, the global rule "
        "is used.",
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    prevent_self_validation = fields.Boolean(default=False)
    expression = fields.Text(
        help="Use this rule only on records where this is true. "
        "Available variables: object, user",
    )
    validator_group_ids = fields.Many2many(
        "res.groups",
        "changeset_field_rule_validator_group_rel",
        string="Validator Groups",
        default=lambda self: self.env.ref(
            "base_changeset.group_changeset_user",
            raise_if_not_found=False,
        )
        or self.env["res.groups"],
    )

    def init(self):
        """Ensure there is at most one rule with source_model_id NULL."""
        self.env.cr.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS source_model_null_field_uniq
                ON %s (field_id)
            WHERE source_model_id IS NULL
        """
            % self._table
        )

    _sql_constraints = [
        (
            "model_field_uniq",
            "unique (source_model_id, field_id)",
            "A rule already exists for this field.",
        )
    ]

    @api.model
    def _domain_source_models(self):
        """Returns the models for which we can define rules.

        Example for submodules (replace by the xmlid of the model):

        ::
            models = super()._domain_source_models()
            return models | self.env.ref('base.model_res_users')

        Rules without model are global and apply for all models.

        """
        return self.env.ref("base.model_res_users")

    @api.model
    def _selection_action(self):
        return [("auto", "Auto"), ("validate", "Validate"), ("never", "Never")]

    @api.constrains("expression")
    def _check_expression(self):
        for this in self:
            this._evaluate_expression(self.env[this.model_id.model].new({}))

    @ormcache(skiparg=1)
    @api.model
    def _get_rules(self, source_model_name, record_model_name):
        """Cache rules

        Keep only the id of the rules, because if we keep the recordsets
        in the ormcache, we won't be able to browse them once their
        cursor is closed.

        The public method ``get_rules`` return the rules with the recordsets
        when called.

        """
        domain = self._get_rules_search_domain(record_model_name, source_model_name)
        model_rules = self.sudo().search(
            domain,
            # using 'ASC' means that 'NULLS LAST' is the default
            order="source_model_id ASC",
        )
        # model's rules have precedence over global ones so we iterate
        # over rules which have a source model first, then we complete
        # them with the global rules
        result = {}
        for rule in model_rules:
            # we already have a model's rule
            if result.get(rule.field_id.name):
                continue
            result[rule.field_id.name] = rule.id
        return result

    def _get_rules_search_domain(self, record_model_name, source_model_name):
        return [
            ("model_id.model", "=", record_model_name),
            "|",
            ("source_model_id.model", "=", source_model_name),
            ("source_model_id", "=", False),
        ]

    @api.model
    def get_rules(self, source_model_name, record_model_name):
        """Return the rules for a model

        When a model is specified, it will return the rules for this
        model.  Fields that have no rule for this model will use the
        global rules (those without source).

        The source model is the model which ask for a change, it will be
        for instance ``res.users``, ``lefac.backend`` or
        ``magellan.backend``.

        The second argument (``source_model_name``) is optional but
        cannot be an optional keyword argument otherwise it would not be
        in the key for the cache. The callers have to pass ``None`` if
        they want only global rules.
        """
        rules = {}
        cached_rules = self._get_rules(source_model_name, record_model_name)
        for field, rule_id in cached_rules.items():
            rules[field] = self.browse(rule_id)
        return rules

    def _evaluate_expression(self, record):
        """Evaluate expression if set"""
        self.ensure_one()
        return not self.expression or tools.safe_eval.safe_eval(
            self.expression, {"object": record, "user": self.env.user}
        )

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        self.clear_caches()
        return record

    def write(self, vals):
        result = super().write(vals)
        self.clear_caches()
        return result

    def unlink(self):
        result = super().unlink()
        self.clear_caches()
        return result
