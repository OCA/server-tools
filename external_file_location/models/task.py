# Copyright 2015 Valentin CHEMIERE @ Akretion
# Copyright @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
import datetime
import logging

from base64 import b64encode
from jinja2 import TemplateError
from jinja2.sandbox import SandboxedEnvironment

from odoo import _, api, fields, models, registry, tools


_logger = logging.getLogger(__name__)


# We use a jinja2 sandboxed environment to render mako templates.
# Note that the rendering does not cover all the mako syntax, in particular
# arbitrary Python statements are not accepted, and not all expressions are
# allowed: only "public" attributes (not starting with '_') of objects may
# be accessed.
# This is done on purpose: it prevents incidental or malicious execution of
# Python code that may break the security of the server.
MAKO_ENV = SandboxedEnvironment(
    variable_start_string="${",
    variable_end_string="}",
    line_statement_prefix="%",
    trim_blocks=True,               # do not output newline after blocks
)
MAKO_ENV.globals.update({
    'str': str,
    'datetime': datetime,
    'len': len,
    'abs': abs,
    'min': min,
    'max': max,
    'sum': sum,
    'round': round,
})


class Task(models.Model):
    _name = 'external.file.task'
    _description = 'External file task'

    name = fields.Char(required=True)
    method_type = fields.Selection(
        [('import', 'Import'), ('export', 'Export')],
        required=True)
    filename = fields.Char(
        help='File name which is imported. '
             'You can use file pattern like *.txt '
             'to import all txt files')
    filepath = fields.Char(
        help='Path to imported/exported file')
    location_id = fields.Many2one(
        'external.file.location', string='Location',
        required=True)
    attachment_ids = fields.One2many(
        'ir.attachment.metadata', 'task_id',
        string='Attachment')
    move_path = fields.Char(
        help='Imported File will be moved to this path')
    new_name = fields.Char(
        help='Imported File will be renamed to this name. '
             'Name can use mako template where obj is an '
             'ir_attachment. Template example : '
             '${obj.name}-${obj.create_date}.csv')
    md5_check = fields.Boolean(
        help='Control file integrity after import with '
             'an MD5 file')
    after_import = fields.Selection(
        selection='_get_action',
        help='Action after import a file')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'external.file.task'))
    file_type = fields.Selection(
        selection=[],
        help="The file type determines an import method to be used "
             "to parse and transform data before their import in ERP")
    active = fields.Boolean(default=True)

    def _get_action(self):
        return [
            ('rename', 'Rename'),
            ('move', 'Move'),
            ('move_rename', 'Move & Rename'),
            ('delete', 'Delete'),
        ]

    @api.multi
    def _prepare_attachment_vals(self, datas, filename, md5_datas):
        self.ensure_one()
        vals = {
            'name': filename,
            'datas': b64encode(datas),
            'datas_fname': filename,
            'task_id': self.id,
            'external_hash': md5_datas,
            'file_type': self.file_type or False,
        }
        return vals

    @api.model
    def _template_render(self, template, record):
        try:
            template = MAKO_ENV.from_string(tools.ustr(template))
        except TemplateError as e:
            _logger.exception(
                _("Failed to load template %r: %s"),
                template, str(e))

        variables = {'obj': record}
        try:
            render_result = template.render(variables)
        except TemplateError as e:
            _logger.exception(
                _("Failed to render template %r using values %r: %s"),
                template, variables, str(e))
            render_result = u""
        if render_result == u"False":
            render_result = u""
        return render_result

    @api.model
    def run_task_scheduler(self, domain=None):
        if domain is None:
            domain = []
        tasks = self.env['external.file.task'].search(domain)
        for task in tasks:
            if task.method_type == 'import':
                task.run_import()
            elif task.method_type == 'export':
                task.run_export()

    @api.multi
    def run_import(self):
        self.ensure_one()
        protocols = self.env['external.file.location']._get_classes()
        cls = protocols.get(self.location_id.protocol)[1]
        attach_obj = self.env['ir.attachment.metadata']
        with cls.connect(self.location_id) as conn:
            md5_datas = ''
            for file_name in conn.listdir(path=self.filepath,
                                          wildcard=self.filename or '',
                                          files_only=True):
                with api.Environment.manage():
                    with registry(self.env.cr.dbname).cursor() as new_cr:
                        new_env = api.Environment(
                            new_cr, self.env.uid, self.env.context)
                        try:
                            full_path = os.path.join(self.filepath, file_name)
                            file_data = conn.open(full_path, 'rb')
                            datas = file_data.read()
                            if self.md5_check:
                                md5_file = conn.open(full_path + '.md5', 'rb')
                                md5_datas = md5_file.read().rstrip('\r\n')
                            attach_vals = self._prepare_attachment_vals(
                                datas, file_name, md5_datas)
                            attachment = attach_obj.with_env(new_env).create(
                                attach_vals)
                            new_full_path = False
                            if self.after_import == 'rename':
                                new_name = self._template_render(
                                    self.new_name, attachment)
                                new_full_path = os.path.join(
                                    self.filepath, new_name)
                            elif self.after_import == 'move':
                                new_full_path = os.path.join(
                                    self.move_path, file_name)
                            elif self.after_import == 'move_rename':
                                new_name = self._template_render(
                                    self.new_name, attachment)
                                new_full_path = os.path.join(
                                    self.move_path, new_name)
                            if new_full_path:
                                conn.rename(full_path, new_full_path)
                                if self.md5_check:
                                    conn.rename(
                                        full_path + '.md5',
                                        new_full_path + '/md5')
                            if self.after_import == 'delete':
                                conn.remove(full_path)
                                if self.md5_check:
                                    conn.remove(full_path + '.md5')
                        except Exception as e:
                            new_env.cr.rollback()
                            raise e
                        else:
                            new_env.cr.commit()

    @api.multi
    def run_export(self):
        self.ensure_one()
        attachment_obj = self.env['ir.attachment.metadata']
        attachments = attachment_obj.search(
            [('task_id', '=', self.id), ('state', '!=', 'done')])
        for attachment in attachments:
            attachment.run()
