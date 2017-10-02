# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
try:
    from slugify import slugify
except ImportError:
    _logger.debug('Cannot `import slugify`.')


def get_model_ref(record):
    return "%s,%s" % (record._name, record.id)


class UrlUrl(models.Model):

    _name = "url.url"

    url_key = fields.Char(required=True)
    model_id = fields.Reference(
        selection=[],
        help="The id of content linked to the url.",
        readonly=True,
        string="Model",
        required=True)
    redirect = fields.Boolean(
        help="If tick this url is a redirection to the new url")
    backend_id = fields.Reference(
        selection=[],
        compute='_compute_related_fields',
        store=True,
        help="Backend linked to this URL",
        string="Backend")
    lang_id = fields.Many2one(
        'res.lang',
        'Lang',
        compute='_compute_related_fields',
        store=True)

    _sql_constraints = [('unique_key_per_backend_per_lang',
                         'unique(url_key, backend_id, lang_id)',
                         'Already exists in database')]

    @api.depends('model_id')
    def _compute_related_fields(self):
        for record in self:
            record.backend_id = get_model_ref(record.model_id.backend_id)
            record.lang_id = record.model_id.lang_id

    @api.model
    def _reference_models(self):
        return []

    def _get_object(self, url):
        """
        :return: return object attach to the url
        """
        return self.search([('url_key', "=", url)]).model_id


class AbstractUrl(models.AbstractModel):
    _name = 'abstract.url'

    url_builder = fields.Selection(
        selection=[
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
            ], default='auto')
    manual_url_key = fields.Char()
    url_key = fields.Char(
        compute='_compute_url',
        store=True)
    redirect_url_key_ids = fields.One2many(
        compute='_compute_redirect_url',
        comodel_name='url.url')

    def _build_url_key(self):
        self.ensure_one()
        return slugify(self.record_id.with_context(
            lang=self.lang_id.code).name)

    @api.model
    def _prepare_url(self, url_key):
        return {
            'url_key': url_key,
            'redirect': False,
            'model_id': get_model_ref(self),
            }

    def set_url(self, url_key):
        """
        backup old url

        1 find url redirect true and same model_id
        if other model id refuse
        2 if exists set to False

        3 write the new one
        """
        self.ensure_one()

        existing_url = self.env['url.url'].search([
            ('url_key', '=', url_key),
            ('backend_id', '=', get_model_ref(self.backend_id)),
            ('lang_id', '=', self.lang_id.id),
            ])
        if existing_url:
            if self != existing_url.model_id:
                raise UserError(
                    _("Url_key already exist in other model"
                      "\n- name: %s\n - id: %s\n"
                      "- url_key: %s\n - url_key_id %s") % (
                          existing_url.model_id.name,
                          existing_url.model_id.record_id.id,
                          existing_url.url_key,
                          existing_url.id,
                          ))
            else:
                existing_url.write({'redirect': False})
        else:
            # no existing key creating one if not empty
            self.env['url.url'].create(self._prepare_url(url_key))
        # other url of object set redirect to True
        redirect_urls = self.env['url.url'].search([
            ('model_id', '=', get_model_ref(self)),
            ('url_key', '!=', url_key),
            ('redirect', '=', False)])
        redirect_urls.write({'redirect': True})

    @api.depends('url_builder')
    def _compute_url(self):
        # We need a clear env before call the set_url method
        # indeed set_url will call a create that will trigger
        # the recomputation of computed field
        # This avoid useless recomputation of field
        # TODO we should see with odoo how we can improve the ORM
        todo = self.env.all.todo
        self.env.all.todo = {}
        for record in self:
            if type(record.record_id.id) == models.NewId\
                    or type(record.id) == models.NewId:
                # Do not update field value on onchange
                # as with_context is broken on NewId
                continue
            if record.url_builder == 'manual':
                new_url = record.manual_url_key
            else:
                new_url = record._build_url_key()
            if new_url:
                record.set_url(new_url)
            record.url_key = new_url
        self.env.all.todo = todo

    def _compute_redirect_url(self):
        for record in self:
            record.redirect_url_key_ids = record.env["url.url"].search([
                ('model_id', '=', get_model_ref(record)),
                ('redirect', '=', True),
                ])

    @api.onchange('manual_url_key')
    def on_url_key_change(self):
        self.ensure_one()
        if self.manual_url_key:
            url = slugify(self.manual_url_key)
            if url != self.manual_url_key:
                self.manual_url_key = url
                return {
                    'warning': {
                        'title': 'Adapt text rules',
                        'message': 'it will be adapted to %s' % url,
                    }}

    def unlink(self):
        for record in self:
            # TODO we should propose to redirect the old url
            urls = record.env["url.url"].search([
                ('model_id', '=', get_model_ref(record)),
                ])
            urls.unlink()
        return super(AbstractUrl, self).unlink()
