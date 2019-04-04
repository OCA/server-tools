# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug('Cannot `import slugify`.')


def get_model_ref(record):
    return "%s,%s" % (record._name, record.id)


class AbstractUrl(models.AbstractModel):
    _name = 'abstract.url'

    url_builder = fields.Selection(
        selection=[
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
            ], default='auto')
    manual_url_key = fields.Char()
    url_key = fields.Char(
        string='Url key',
        compute='_compute_url',
        store=True,
    )
    url_url_ids = fields.One2many(
        compute='_compute_url_url_ids',
        comodel_name='url.url')
    redirect_url_key_ids = fields.One2many(
        compute='_compute_redirect_url',
        comodel_name='url.url')
    lang_id = fields.Many2one(
        'res.lang',
        string='Lang',
        required=True)
    is_urls_sync_required = fields.Boolean(
        compute="_compute_is_urls_sync_required",
        store=True,
    )
    active = fields.Boolean(string="Active", default=True)

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

    def _reuse_url(self, existing_url):
        # TODO add user notification in the futur SEO dashboard
        existing_url.write({
            'model_id': get_model_ref(self),
            'redirect': False,
        })

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
                if existing_url.redirect:
                    self._reuse_url(existing_url)
                else:
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

    def _redirect_existing_url(self):
        return True

    @api.depends('url_builder', 'manual_url_key', 'active')
    def _compute_is_urls_sync_required(self):
        for record in self:
            record.is_urls_sync_required = True

    @api.depends('url_builder', 'manual_url_key', 'active')
    def _compute_url(self):
        for record in self:
            if type(record.record_id.id) == models.NewId\
                    or type(record.id) == models.NewId:
                # Do not update field value on onchange
                # as with_context is broken on NewId
                continue
            if not record.active:
                record.url_key = ''
            else:
                if record.url_builder == 'manual':
                    new_url = record.manual_url_key
                else:
                    new_url = record._build_url_key()
                record.url_key = new_url

    def _compute_redirect_url(self):
        for record in self:
            record.redirect_url_key_ids = record.env["url.url"].search([
                ('model_id', '=', get_model_ref(record)),
                ('redirect', '=', True),
                ])

    def _compute_url_url_ids(self):
        for record in self:
            record.url_url_ids = record.env["url.url"].search([
                ('model_id', '=', get_model_ref(record)),
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

    @api.multi
    def _sync_urls(self):
        """
        This method is in charge of syncing the url.url object related to
        the current model
        """
        records = self.filtered("is_urls_sync_required")
        for record in records:
            if not record.active:
                record._redirect_existing_url()
            else:
                record.set_url(record.url_key)
        return records

    @api.multi
    def write(self, value):
        res = super(AbstractUrl, self).write(value)
        synced = self._sync_urls()
        super(AbstractUrl, synced).write({"is_urls_sync_required": False})
        return res

    @api.multi
    def unlink(self):
        for record in self:
            # TODO we should propose to redirect the old url
            urls = record.env["url.url"].search([
                ('model_id', '=', get_model_ref(record)),
                ])
            urls.unlink()
        return super(AbstractUrl, self).unlink()
