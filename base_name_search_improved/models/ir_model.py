# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from ast import literal_eval

from lxml import etree

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)
# Extended name search is only used on some operators
ALLOWED_OPS = {"ilike", "like"}


@tools.ormcache(skiparg=0)
def _get_rec_names(self):
    "List of fields to search into"
    model = self.env["ir.model"].search([("model", "=", str(self._name))])
    rec_name = [self._rec_name] or []
    other_names = model.name_search_ids.mapped("name")
    return rec_name + other_names


@tools.ormcache(skiparg=0)
def _get_use_smart_name_search(self):
    return (
        self.env["ir.model"]
        .search([("model", "=", str(self._name))])
        .use_smart_name_search
    )


@tools.ormcache(skiparg=0)
def _get_add_smart_search(self):
    "Add Smart Search on search views"
    model = self.env["ir.model"].search([("model", "=", str(self._name))])
    # Run only if module is installed
    if hasattr(model, "add_smart_search"):
        return model.add_smart_search
    return False


@tools.ormcache(skiparg=0)
def _get_name_search_domain(self):
    "Add Smart Search on search views"
    name_search_domain = (
        self.env["ir.model"]
        .search([("model", "=", str(self._name))])
        .name_search_domain
    )
    if name_search_domain:
        return literal_eval(name_search_domain)
    return []


def _extend_name_results(self, domain, results, limit):
    result_count = len(results)
    if result_count < limit:
        domain += [("id", "not in", results)]
        rec_ids = self._search(
            domain,
            limit=limit - result_count,
        )
        results.extend(rec_ids)
    return results


class Base(models.AbstractModel):
    _inherit = "base"

    # TODO perhaps better to create only the field when enabled on the model
    smart_search = fields.Char(
        compute="_compute_smart_search", search="_search_smart_search", translate=False
    )

    def _compute_smart_search(self):
        self.smart_search = False

    @api.model
    def _search_smart_search(self, operator, value):
        if value and operator in ALLOWED_OPS:
            matching_records = self.with_context(
                force_smart_name_search=True
            ).name_search(name=value, operator=operator)
            if matching_records:
                record_ids = [record[0] for record in matching_records]
                return [("id", "in", record_ids)]
        return [("id", "=", False)]

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)
        if self.env.context.get(
            "force_smart_name_search", False
        ) or _get_use_smart_name_search(self.sudo()):
            all_names = _get_rec_names(self.sudo())
            additional_domain = _get_name_search_domain(self.sudo())

            for word in value.split():
                word_domain = []
                for rec_name in all_names:
                    word_domain = (
                        word_domain and ["|"] + word_domain or word_domain
                    ) + [(rec_name, operator, word)]
                additional_domain = (
                    additional_domain and ["&"] + additional_domain or additional_domain
                ) + word_domain

            return expression.OR([additional_domain, domain])

        return domain

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if not name or not (
            self.env.context.get("force_smart_name_search", False)
            or _get_use_smart_name_search(self.sudo())
        ):
            return super().name_search(name, args, operator, limit)

        # Support a list of fields to search on
        all_names = _get_rec_names(self.sudo())
        base_domain = args or []
        limit = limit or 0
        results = []

        # Try regular search on each additional search field
        for rec_name in all_names:
            domain = expression.AND([base_domain, [(rec_name, operator, name)]])
            results = _extend_name_results(self, domain, results, limit)

        # Try ordered word search on each of the search fields
        for rec_name in all_names:
            domain = expression.AND(
                [base_domain, [(rec_name, operator, name.replace(" ", "%"))]]
            )
            results = _extend_name_results(self, domain, results, limit)

        # Try unordered word search on each of the search fields
        # we only perform this search if we have at least one
        # separator character
        if " " in name:
            unordered_domain = []
            for word in name.split():
                word_domain = expression.OR(
                    [[(rec_name, operator, word)] for rec_name in all_names]
                )
                unordered_domain = (
                    expression.AND([unordered_domain, word_domain])
                    if unordered_domain
                    else word_domain
                )
            results = _extend_name_results(
                self, expression.AND([base_domain, unordered_domain]), results, limit
            )

        results = results[:limit]
        records = self.browse(results)
        return [(record.id, record.display_name) for record in records]

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "search" and _get_add_smart_search(self.sudo()):
            placeholders = arch.xpath("//search/field")
            if placeholders:
                placeholder = placeholders[0]
            else:
                placeholder = arch.xpath("//search")[0]
            placeholder.addnext(etree.Element("field", {"name": "smart_search"}))
            arch.remove(placeholder)
        return arch, view


class IrModel(models.Model):
    _inherit = "ir.model"

    add_smart_search = fields.Boolean(help="Add Smart Search on search views")
    use_smart_name_search = fields.Boolean(
        string="Smart Name Search Enabled?",
        help="Use Smart Search for 'name_search', this will affect when "
        "searching from other records (for eg. from m2o fields",
    )
    name_search_ids = fields.Many2many("ir.model.fields", string="Smart Search Fields")
    name_search_domain = fields.Char(string="Smart Search Domain")
    smart_search_warning = fields.Html(compute="_compute_smart_search_warning")

    @api.depends("name_search_ids")
    def _compute_smart_search_warning(self):
        msgs = []
        for rec in self:
            if len(rec.name_search_ids) > 4:
                msgs.append(
                    "You have selected more than 4 fields for smart search, "
                    "fewerer fields is recommended"
                )
            if any(x.translate for x in rec.name_search_ids):
                msgs.append(
                    "You have selected translatable fields in the smart search,"
                    " try to avoid them if possible"
                )
            # rec.smart_search_warning = msg
            if msgs:
                rec.smart_search_warning = (
                    f"<p>In case of performance issues we recommend to review "
                    f"these suggestions: <ul>"
                    f"{''.join(f'<li>{x}</li>' for x in msgs)}</ul></p>"
                )
            else:
                rec.smart_search_warning = False

    @api.constrains("name_search_ids", "name_search_domain", "add_smart_search")
    def update_search_wo_restart(self):
        self.env.registry.clear_cache()

    @api.constrains("name_search_domain")
    def check_name_search_domain(self):
        for rec in self.filtered("name_search_domain"):
            name_search_domain = False
            try:
                name_search_domain = literal_eval(rec.name_search_domain)
            except (
                ValueError,
                TypeError,
                SyntaxError,
                MemoryError,
                RecursionError,
            ) as e:
                raise ValidationError(
                    self.env._("Couldn't eval Name Search Domain (%s)") % e
                ) from e
            if not isinstance(name_search_domain, list):
                raise ValidationError(
                    self.env._("Name Search Domain must be a list of tuples")
                )

    def write(self, vals):
        if "add_smart_search" in vals:
            self.env.registry.clear_cache("templates")
        return super().write(vals)

    def _register_hook(self):
        def make_smart_name_search(original_name_search):
            def wrapper(
                self, name="", args=None, operator="ilike", limit=100, **kwargs
            ):
                original_results = original_name_search(
                    self, name, args, operator, limit, **kwargs
                )
                if not name or (limit and len(original_results) >= limit):
                    return original_results
                seen_ids = {res[0] for res in original_results}
                remaining_limit = limit - len(original_results) if limit else None
                smart_results = Base.name_search(
                    self, name=name, args=args, operator=operator, limit=remaining_limit
                )
                additional_results = [
                    (res_id, res_name)
                    for res_id, res_name in smart_results
                    if res_id not in seen_ids
                ]
                return original_results + additional_results

            wrapper._is_smart_patched = True
            wrapper.origin = original_name_search
            wrapper._api = getattr(original_name_search, "_api", None)
            return wrapper

        model_records = self.env["ir.model"].search(
            [("use_smart_name_search", "=", True)]
        )
        for model_record in model_records:
            ModelClass = self.env.registry[model_record.model]
            if not hasattr(ModelClass, "name_search"):
                continue

            original_name_search = ModelClass.name_search
            if getattr(original_name_search, "_is_smart_patched", False):
                continue

            ModelClass.name_search = make_smart_name_search(original_name_search)

        return super()._register_hook()
