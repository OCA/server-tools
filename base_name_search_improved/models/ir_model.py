# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from ast import literal_eval

from lxml import etree

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

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


def _extend_name_results(self, domain, results, limit, name_get_uid):
    result_count = len(results)
    if result_count < limit:
        domain += [("id", "not in", results)]
        rec_ids = self._search(
            domain, limit=limit - result_count, access_rights_uid=name_get_uid
        )
        results.extend(rec_ids)
    return results


def patch_name_search():
    @api.model
    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        # Perform standard name search
        res = _name_search.origin(
            self,
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )
        if name and _get_use_smart_name_search(self.sudo()) and operator in ALLOWED_OPS:
            limit = limit or 0

            # we add domain
            args = args or [] + _get_name_search_domain(self.sudo())

            # Support a list of fields to search on
            all_names = _get_rec_names(self.sudo())
            base_domain = args or []
            # Try regular search on each additional search field
            for rec_name in all_names[1:]:
                domain = [(rec_name, operator, name)]
                res = _extend_name_results(
                    self, base_domain + domain, res, limit, name_get_uid
                )
            # Try ordered word search on each of the search fields
            for rec_name in all_names:
                domain = [(rec_name, operator, name.replace(" ", "%"))]
                res = _extend_name_results(
                    self, base_domain + domain, res, limit, name_get_uid
                )
            # Try unordered word search on each of the search fields
            # we only perform this search if we have at least one
            # separator character
            # also, if have raise the limit we skeep this iteration
            if " " in name and len(res) < limit:
                domain = []
                for word in name.split():
                    word_domain = []
                    for rec_name in all_names:
                        word_domain = (
                            word_domain and ["|"] + word_domain or word_domain
                        ) + [(rec_name, operator, word)]
                    domain = (domain and ["&"] + domain or domain) + word_domain
                res = _extend_name_results(
                    self, base_domain + domain, res, limit, name_get_uid
                )

        return res

    return _name_search


def patch_fields_view_get():
    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = fields_view_get.origin(
            self,
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "search" and _get_add_smart_search(self):
            eview = etree.fromstring(res["arch"])
            placeholders = eview.xpath("//search/field")
            if placeholders:
                placeholder = placeholders[0]
            else:
                placeholder = eview.xpath("//search")[0]
            placeholder.addnext(etree.Element("field", {"name": "smart_search"}))
            eview.remove(placeholder)
            res["arch"] = etree.tostring(eview)
            res["fields"].update(self.fields_get(["smart_search"]))
        return res

    return fields_view_get


class Base(models.AbstractModel):

    _inherit = "base"

    # TODO perhaps better to create only the field when enabled on the model
    smart_search = fields.Char(
        compute="_compute_smart_search",
        search="_search_smart_search",
    )

    def _compute_smart_search(self):
        self.smart_search = False

    @api.model
    def _search_smart_search(self, operator, value):
        """
        For now this method does not call
        self._name_search(name, operator=operator) since it is not as
        performant if unlimited records are called which is what name
        search should return. That is why it is reimplemented here
        again. In addition, name_search has a logic which first tries
        to return best match, which in this case is not necessary.
        Surely, it can be improved and a lot of code can be unified.
        """
        name = value
        if name and operator in ALLOWED_OPS:
            all_names = _get_rec_names(self.sudo())
            domain = _get_name_search_domain(self.sudo())
            for word in name.split():
                word_domain = []
                for rec_name in all_names:
                    word_domain = (
                        word_domain and ["|"] + word_domain or word_domain
                    ) + [(rec_name, operator, word)]
                domain = (domain and ["&"] + domain or domain) + word_domain
            return domain
        return []


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
                    "<p>In case of performance issues we recommend to review "
                    "these suggestions: <ul>%s</ul></p>"
                ) % "".join(["<li>%s</li>" % x for x in msgs])
            else:
                rec.smart_search_warning = False

    @api.constrains("name_search_ids", "name_search_domain", "add_smart_search")
    def update_search_wo_restart(self):
        self.clear_caches()

    @api.constrains("name_search_domain")
    def check_name_search_domain(self):
        for rec in self.filtered("name_search_domain"):
            name_search_domain = False
            try:
                name_search_domain = literal_eval(rec.name_search_domain)
            except Exception as error:
                raise ValidationError(
                    _("Couldn't eval Name Search Domain (%s)") % error
                )
            if not isinstance(name_search_domain, list):
                raise ValidationError(_("Name Search Domain must be a list of tuples"))

    def _register_hook(self):

        _logger.info("Patching BaseModel for Smart Search")
        models.BaseModel._patch_method("fields_view_get", patch_fields_view_get())

        for model in self.sudo().search(self.ids or []):
            Model = self.env.get(model.model)
            if Model is not None:
                Model._patch_method("_name_search", patch_name_search())

        return super(IrModel, self)._register_hook()
