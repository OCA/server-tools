# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import logging
import os
from fnmatch import fnmatch

import odoo
from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        variable_start_string="${",
        variable_end_string="}",
        line_statement_prefix="%",
        trim_blocks=True,               # do not output newline after blocks
    )
    mako_template_env.globals.update({
        'str': str,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'map': map,
        'round': round,
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class StorageTask(models.Model):
    _name = 'storage.backend.task'
    _description = 'Storage Backend task'

    name = fields.Char(required=True)
    method_type = fields.Selection(
        [('import', 'Import'), ('export', 'Export')],
        required=True)
    filename = fields.Char(help='File name which is imported.'
                                'The system will check if the remote file at '
                                'least contains the pattern in its name. '
                                'Leave it empty to import all files')
    filepath = fields.Char(help='Path to imported/exported file')
    backend_id = fields.Many2one(
        'storage.backend', string='Backend', required=True)
    attachment_ids = fields.One2many('ir.attachment.metadata', 'task_id',
                                     string='Attachment')
    move_path = fields.Char(string='Move Path',
                            help='Imported File will be moved to this path')
    new_name = fields.Char(string='New Name',
                           help='Imported File will be renamed to this name\n'
                                'Name can use mako template where obj is an '
                                'ir_attachement. template exemple : '
                                '  ${obj.name}-${obj.create_date}.csv')
    after_import = fields.Selection(
        selection=[
            ('rename', 'Rename'),
            ('move', 'Move'),
            ('move_rename', 'Move & Rename'),
            ('delete', 'Delete'),
        ], help='Action after import a file')
    file_type = fields.Selection(
        selection=[],
        string="File Type",
        help="The file type determines an import method to be used "
             "to parse and transform data before their import in ERP")
    active = fields.Boolean(default=True)

    @api.multi
    def _prepare_attachment_vals(self, datas, filename):
        self.ensure_one()
        vals = {
            'name': filename,
            'datas': datas,
            'datas_fname': filename,
            'task_id': self.id,
            'file_type': self.file_type or False,
        }
        return vals

    @api.model
    def _template_render(self, template, record):
        try:
            template = mako_template_env.from_string(tools.ustr(template))
        except Exception:
            _logger.exception("Failed to load template %r", template)

        variables = {'obj': record}
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.exception(
                "Failed to render template %r using values %r" %
                (template, variables))
            render_result = u""
        if render_result == u"False":
            render_result = u""
        return render_result

    @api.model
    def run_task_scheduler(self, domain=list()):
        if ('method_type', '=', 'import') not in domain:
            domain.append([('method_type', '=', 'import')])

        tasks = self.env['storage.backend'].search(domain)
        for task in tasks:
            task.run_import()

    @api.multi
    def run_import(self):
        self.ensure_one()
        attach_obj = self.env['ir.attachment.metadata']
        backend = self.backend_id
        all_filenames = backend._list(relative_path=self.filepath)
        if self.filename:
            filenames = [x for x in all_filenames if fnmatch(x, self.filename)]
        for file_name in filenames:
            with api.Environment.manage():
                with odoo.registry(
                        self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid,
                                              self.env.context)
                    try:
                        full_absolute_path = os.path.join(
                            self.filepath, file_name)
                        datas = backend._get_b64_data(full_absolute_path)
                        attach_vals = self._prepare_attachment_vals(
                            datas, file_name)
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
                            backend._add_b64_data(new_full_path, datas)
                        if self.after_import in (
                                'delete', 'rename', 'move', 'move_rename'
                        ):
                            backend._delete(full_absolute_path)
                    except Exception as e:
                        new_env.cr.rollback()
                        raise e
                    else:
                        new_env.cr.commit()
