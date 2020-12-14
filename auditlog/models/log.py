# -*- coding: utf-8 -*-
# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models, fields
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class AuditlogLog(models.Model):
    _name = 'auditlog.log'
    _description = "Auditlog - Log"
    _order = "create_date desc"

    name = fields.Char("Resource Name", size=64)
    model_id = fields.Many2one(
        'ir.model', string=u"Model", index=True, on_delete='set null')
    model_name = fields.Char(string=u'Model Name')
    model_model = fields.Char(string=u'Technical Model Name')
    res_id = fields.Integer(u"Resource ID")
    user_id = fields.Many2one(
        'res.users', string=u"User")
    method = fields.Char(u"Method", size=64)
    line_ids = fields.One2many(
        'auditlog.log.line', 'log_id', string=u"Fields updated")
    http_session_id = fields.Many2one(
        'auditlog.http.session', string=u"Session")
    http_request_id = fields.Many2one(
        'auditlog.http.request', string=u"HTTP Request")
    log_type = fields.Selection(
        [('full', u"Full log"),
         ('fast', u"Fast log"),
         ],
        string=u"Type")

    @api.model
    def create(self, vals):
        """ Insert model_name and model_model field values upon creation. """
        if 'model_id' in vals and vals['model_id']:
            model = self.env['ir.model'].browse(vals['model_id'])
            vals.update({'model_name': model.name,
                         'model_model': model.model})
        return super(AuditlogLog, self).create(vals)

    @api.multi
    def write(self, vals):
        """ Update model_name and model_model field values to reflect model_id
        changes. """
        if 'model_id' in vals and vals['model_id']:
            model = self.env['ir.model'].browse(vals['model_id'])
            vals.update({'model_name': model.name,
                         'model_model': model.model})
        return super(AuditlogLog, self).write(vals)


class AuditlogLogLine(models.Model):
    _name = 'auditlog.log.line'
    _description = "Auditlog - Log details (fields updated)"

    field_id = fields.Many2one(
        'ir.model.fields', ondelete='set null', string=u"Field", index=True)
    log_id = fields.Many2one(
        'auditlog.log', string=u"Log", ondelete='cascade', index=True)
    old_value = fields.Text(u"Old Value")
    new_value = fields.Text(u"New Value")
    old_value_text = fields.Text(u"Old value Text")
    new_value_text = fields.Text(u"New value Text")
    field_name = fields.Char(u"Technical name")
    field_description = fields.Char(u"Description")

    @api.model
    def create(self, vals):
        """ Ensure field_id is not empty on creation and store field_name and
        field_description. """
        if 'field_id' not in vals or not vals['field_id']:
            raise UserError(_("No field defined to create line."))
        field = self.env['ir.model.fields'].browse(vals['field_id'])
        vals.update({'field_name': field.name,
                     'field_description': field.field_description})
        return super(AuditlogLogLine, self).create(vals)

    @api.multi
    def write(self, vals):
        """ Ensure field_id is set during write and update field_name and
        field_description values. """
        if 'field_id' in vals:
            if not vals['field_id']:
                raise UserError(_("The field 'field_id' cannot be empty."))
            field = self.env['ir.model.fields'].browse(vals['field_id'])
            vals.update({'field_name': field.name,
                         'field_description': field.field_description})
        return super(AuditlogLogLine, self).write(vals)
