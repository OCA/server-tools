# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, models, tools
from odoo.osv import expression


class Base(models.AbstractModel):
    _inherit = "base"

    @tools.ormcache("self._name")
    def _name_search_multi_lang_enabled(self):
        """Whether this model is searched in all the installed languages"""
        data = (
            self.env["ir.model"]
            .sudo()
            .search_read([("model", "=", self._name)], ["name_search_multi_lang"])
        )
        return bool(data and data[0]["name_search_multi_lang"])

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        if (
            not name
            # A name of another language never matches a negative condition on
            # the name of the current language
            or operator in expression.NEGATIVE_TERM_OPERATORS
            # Avoid recursion when searching the other languages below
            or self.env.context.get("name_search_multi_lang_done")
            or not self._name_search_multi_lang_enabled()
            or (limit and len(res) >= limit)
        ):
            return res
        ids = [rec_id for rec_id, _name in res]
        langs = [
            code
            for code, _name in self.env["res.lang"].get_installed()
            if code != self.env.lang
        ]
        for lang in langs:
            model_lang = self.with_context(lang=lang, name_search_multi_lang_done=True)
            for rec_id, _name in model_lang.name_search(
                name=name, args=args, operator=operator, limit=limit
            ):
                if rec_id not in ids:
                    ids.append(rec_id)
            if limit and len(ids) >= limit:
                break
        if len(ids) == len(res):
            return res
        # Return the names in the language of the user
        records = self.browse(ids[:limit] if limit else ids).sudo()
        return [(record.id, record.display_name) for record in records]
