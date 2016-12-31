# -*- coding: utf-8 -*-
# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from openerp import tools
from lxml import etree
from ast import literal_eval
from openerp.exceptions import ValidationError

# Extended name search is only used on some operators
ALLOWED_OPS = set(['ilike', 'like'])


@tools.ormcache(skiparg=0)
def _get_rec_names(self):
    "List of fields to search into"
    model = self.env['ir.model'].search(
        [('model', '=', str(self._model))])
    rec_name = [self._rec_name] or []
    other_names = model.name_search_ids.mapped('name')
    return rec_name + other_names


@tools.ormcache(skiparg=0)
def _get_rec_exact_names(self):
    "List of fields to exact search into"
    model = self.env['ir.model'].search(
        [('model', '=', str(self._model))])
    other_names = model.name_search_exact_ids.mapped('name')
    return other_names


@tools.ormcache(skiparg=0)
def _get_add_smart_search(self):
    "Add Smart Search on search views"
    return self.env['ir.model'].search(
        [('model', '=', str(self._model))]).add_smart_search


@tools.ormcache(skiparg=0)
def _get_name_search_domain(self):
    "Add Smart Search on search views"
    name_search_domain = self.env['ir.model'].search(
        [('model', '=', str(self._model))]).name_search_domain
    if name_search_domain:
        return literal_eval(name_search_domain)
    return []


def _get_separator(self):
    return self.env['ir.config_parameter'].get_param(
        'base_name_search_improved.separator', default=" ")


def _extend_name_results(self, domain, results, limit):
    result_count = len(results)
    if result_count < limit:
        domain += [('id', 'not in', [x[0] for x in results])]
        recs = self.search(domain, limit=limit - result_count)
        results.extend(recs.name_get())
    return results

# TODO move all this to register_hook


_add_magic_fields_original = models.BaseModel._add_magic_fields


@api.model
def _add_magic_fields(self):
    res = _add_magic_fields_original(self)

    if (
            'base_name_search_improved' in self.env.registry._init_modules and
            'smart_search' not in self._fields):
        self._add_field('smart_search', fields.Char(
            automatic=True, compute='_compute_smart_search',
            search='_search_smart_search'))
    return res


models.BaseModel._add_magic_fields = _add_magic_fields


class ModelExtended(models.Model):
    _inherit = 'ir.model'

    add_smart_search = fields.Boolean(
        help="Add Smart Search on search views"
    )
    name_search_ids = fields.Many2many(
        'ir.model.fields',
        string='Name Search Fields')
    name_search_exact_ids = fields.Many2many(
        'ir.model.fields',
        'ir_model_name_search_exact_rel',
        'model_id', 'field_id',
        string='Name Search Exact Fields',
        help="If we found exact matches for this fields then we return only "
        "this results and we don't keep going")
    name_search_domain = fields.Char()

    @api.multi
    @api.constrains('name_search_domain')
    def check_name_search_domain(self):
        for rec in self.filtered('name_search_domain'):
            name_search_domain = False
            try:
                name_search_domain = literal_eval(rec.name_search_domain)
            except Exception, e:
                raise ValidationError(_(
                    "Couldn't eval Name Search Domain (%s)") % e)
            if not isinstance(name_search_domain, list):
                raise ValidationError(_(
                    'Name Search Domain must be a list of tuples'))

    def _register_hook(self, cr, ids=None):
        def make_name_search():

            @api.model
            def name_search(self, name='', args=None,
                            operator='ilike', limit=100):
                enabled = self.env.context.get('name_search_extended', True)
                if enabled:
                    # we add domain
                    args = args or [] + _get_name_search_domain(self)

                # first we search for an exact match, if we found any, we
                # return it
                if name and enabled and operator in ALLOWED_OPS:
                    exact_fields_names = _get_rec_exact_names(self)
                    for rec_name in exact_fields_names:
                        recs = self.search(
                            args + [(rec_name, '=ilike', name)], limit=limit)
                        if recs:
                            return recs.name_get()

                # Perform standard name search
                res = name_search.origin(
                    self, name=name, args=args, operator=operator, limit=limit)
                # Perform extended name search
                # Note: Empty name causes error on
                #       Customer->More->Portal Access Management
                if name and enabled and operator in ALLOWED_OPS:
                    # Support a list of fields to search on
                    all_names = _get_rec_names(self)
                    base_domain = args or []
                    # Try regular search on each additional search field
                    for rec_name in all_names[1:]:
                        domain = [(rec_name, operator, name)]
                        res = _extend_name_results(
                            self, base_domain + domain, res, limit)
                    # Try ordered word search on each of the search fields
                    for rec_name in all_names:
                        domain = [(rec_name, operator, name.replace(' ', '%'))]
                        res = _extend_name_results(
                            self, base_domain + domain, res, limit)

                    # Try unordered word search on each of the search fields
                    # we only perform this search if we have at least one
                    # separator character
                    separator = _get_separator(self)
                    if separator in name:
                        domain = []
                        for word in name.split(separator):
                            word_domain = []
                            for rec_name in all_names:
                                word_domain = (
                                    word_domain and ['|'] + word_domain or
                                    word_domain
                                ) + [(rec_name, operator, word)]
                            domain = (
                                domain and ['&'] + domain or domain
                            ) + word_domain
                        res = _extend_name_results(
                            self, base_domain + domain, res, limit)

                return res
            return name_search

        def patch_fields_view_get():
            @api.model
            def fields_view_get(
                    self, view_id=None, view_type=False, toolbar=False,
                    submenu=False):
                res = fields_view_get.origin(
                    self, view_id=view_id, view_type=view_type,
                    toolbar=toolbar, submenu=submenu)
                if view_type == 'search' and _get_add_smart_search(self):
                    eview = etree.fromstring(res['arch'])
                    placeholders = eview.xpath("//search/field")
                    if placeholders:
                        placeholder = placeholders[0]
                    else:
                        placeholder = eview.xpath("//search")[0]
                    placeholder.addnext(
                        etree.Element('field', {'name': 'smart_search'}))
                    eview.remove(placeholder)
                    res['arch'] = etree.tostring(eview)
                    res['fields'].update(self.fields_get(['smart_search']))
                return res
            return fields_view_get

        # def patch_add_magic_fields():
        #     @api.model
        #     def _add_magic_fields(self):
        #         res = _add_magic_fields.origin(self)
        #         if 'smart_search' not in self._fields:
        #             self._add_field('smart_search', fields.Char(
        #                 automatic=True, compute='_compute_smart_search',
        #                 search='_search_smart_search'))
        #         return res
        #     return _add_magic_fields

        @api.multi
        def _compute_smart_search(self):
            return False

        @api.model
        def _search_smart_search(self, operator, value):
            enabled = self.env.context.get('name_search_extended', True)
            name = value
            if name and enabled and operator in ALLOWED_OPS:
                exact_fields_names = _get_rec_exact_names(self)
                for rec_name in exact_fields_names:
                    recs = self.search([(rec_name, '=ilike', name)])
                    if recs:
                        return [(rec_name, '=ilike', name)]

                all_names = _get_rec_names(self)
                domain = _get_name_search_domain(self)
                for word in name.split(_get_separator(self)):
                    word_domain = []
                    for rec_name in all_names:
                        word_domain = (
                            word_domain and ['|'] + word_domain or
                            word_domain
                        ) + [(rec_name, operator, word)]
                    domain = (
                        domain and ['&'] + domain or domain
                    ) + word_domain
                return domain
            return []

        # add methods of computed fields
        if not hasattr(models.BaseModel, '_compute_smart_search'):
            models.BaseModel._compute_smart_search = _compute_smart_search
        if not hasattr(models.BaseModel, '_search_smart_search'):
            models.BaseModel._search_smart_search = _search_smart_search

        if ids is None:
            ids = self.search(cr, SUPERUSER_ID, [])
        for model in self.browse(cr, SUPERUSER_ID, ids):
            Model = self.pool.get(model.model)
            if Model:
                Model._patch_method(
                    'name_search', make_name_search())
                Model._patch_method(
                    'fields_view_get', patch_fields_view_get())
                # TODO improove this, not sure why but it dones works when
                # patching this way
                # Model._patch_method(
                #     '_add_magic_fields', patch_add_magic_fields())

        return super(ModelExtended, self)._register_hook(cr)
