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
        domain += [("id", "not in", [x[0] for x in results])]
        recs = self.search(domain, limit=limit - result_count)
        results.extend(recs.name_get())
    return results


def patch_name_search():
    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        limit = limit or 0
        enabled = self.env.context.get("name_search_extended", True)
        superself = self.sudo()
        if enabled:
            # we add domain
            args = args or [] + _get_name_search_domain(superself)
        # Perform standard name search
        res = name_search.origin(
            self, name=name, args=args, operator=operator, limit=limit
        )
        # Perform extended name search
        # Note: Empty name causes error on
        #       Customer->More->Portal Access Management
        if name and enabled and operator in ALLOWED_OPS:
            # Support a list of fields to search on
            all_names = _get_rec_names(superself)
            base_domain = args or []
            # Try regular search on each additional search field
            for rec_name in all_names[1:]:
                domain = [(rec_name, operator, name)]
                res = _extend_name_results(self, base_domain + domain, res, limit)
            # Try ordered word search on each of the search fields
            for rec_name in all_names:
                domain = [(rec_name, operator, name.replace(" ", "%"))]
                res = _extend_name_results(self, base_domain + domain, res, limit)
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
                res = _extend_name_results(self, base_domain + domain, res, limit)

        return res

    return name_search


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
        Por ahora este método no llama a
        self.name_search(name, operator=operator) ya que este no es tan
        performante si se llama a ilimitados registros que es lo que el
        name search debe devolver. Por eso se reimplementa acá nuevamente.
        Además name_search tiene una lógica por la cual trata de devolver
        primero los que mejor coinciden, en este caso eso no es necesario
        Igualmente seguro se puede mejorar y unificar bastante código
        """
        enabled = self.env.context.get("name_search_extended", True)
        name = value
        if name and enabled and operator in ALLOWED_OPS:
            superself = self.sudo()
            all_names = _get_rec_names(superself)
            domain = _get_name_search_domain(superself)
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

    add_smart_search = fields.Boolean(
        help="Add Smart Search on search views",
    )
    name_search_ids = fields.Many2many("ir.model.fields", string="Name Search Fields")
    name_search_domain = fields.Char()

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

        _logger.info("Patching fields_view_get on BaseModel")
        models.BaseModel._patch_method("fields_view_get", patch_fields_view_get())

        for model in self.sudo().search(self.ids or []):
            Model = self.env.get(model.model)
            if Model is not None:
                Model._patch_method("name_search", patch_name_search())

        return super(IrModel, self)._register_hook()

    def toggle_smart_search(self):
        """Inverse the value of the field ``add_smart_search`` on the records
        in ``self``."""
        for record in self:
            record.add_smart_search = not record.add_smart_search
