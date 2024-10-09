# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models, tools


@tools.ormcache("model")
def _get_model_name_search_multi_lang(self, model):
    multi_lang = self.env["ir.model"].search_read(
        [("model", "=", self._name)], ["name_search_multi_lang"]
    )[0]["name_search_multi_lang"]
    return multi_lang


def _extend_name_search_lang(self, lang, name, args, operator, result, limit):
    res_lang = list(
        self.with_context(lang=lang)._name_search(name, args, operator, limit=limit)
    )
    new_res = list(filter(lambda x: x not in result, res_lang))
    result.extend(new_res)
    return result


class IrModel(models.Model):
    _inherit = "ir.model"

    name_search_multi_lang = fields.Boolean(
        string="Search Translated Name",
        help="Name search this model from all translated languages",
    )

    @api.constrains("name_search_multi_lang")
    def update_name_search_multi_lang(self):
        self.clear_caches()

    def _register_hook(self):
        def make_name_search():
            @api.model
            def name_search(self, name="", args=None, operator="ilike", limit=100):
                res = name_search.origin(
                    self, name=name, args=args, operator=operator, limit=limit
                )
                res_ids = [x[0] for x in res]
                # For model with name_search_multi_lang, extend result
                multi_lang = _get_model_name_search_multi_lang(self, self._name)
                if multi_lang:
                    context_lang = self._context.get("lang")
                    installed_langs = self.env["res.lang"].get_installed()
                    langs = [x[0] for x in installed_langs if x[0] != context_lang]
                    for lang in langs:
                        res_ids = _extend_name_search_lang(
                            self, lang, name, args, operator, res_ids, limit
                        )
                    domain = [("id", "in", [x for x in res_ids])]
                    _ids = self._search(domain, limit=limit)
                    res = models.lazy_name_get(self.browse(_ids))
                return res

            return name_search

        for model in self.sudo().search(self.ids or []):
            Model = self.env.get(model.model)
            if Model is not None:
                Model._patch_method("name_search", make_name_search())

        return super(IrModel, self)._register_hook()
