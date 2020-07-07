# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import logging
import os

import odoo
from odoo import api, fields, models, tools
from odoo.osv import expression

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
        trim_blocks=True,  # do not output newline after blocks
    )
    mako_template_env.globals.update(
        {
            "str": str,
            "datetime": datetime,
            "len": len,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "filter": filter,
            "map": map,
            "round": round,
        }
    )
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class AttachmentSynchronizeTask(models.Model):
    _name = "attachment.synchronize.task"
    _description = "Attachment synchronize task"

    name = fields.Char(required=True)
    method_type = fields.Selection(
        [("import", "Import"), ("export", "Export")], required=True
    )
    pattern = fields.Char(
        help="File name which is imported."
        "The system will check if the remote file at "
        "least contains the pattern in its name. "
        "Leave it empty to import all files"
    )
    filepath = fields.Char(
        string="File Path", help="Path to imported/exported files in the Backend"
    )
    backend_id = fields.Many2one("storage.backend", string="Backend")
    attachment_ids = fields.One2many("attachment.queue", "task_id", string="Attachment")
    move_path = fields.Char(
        string="Move Path", help="Imported File will be moved to this path"
    )
    new_name = fields.Char(
        string="New Name",
        help="Imported File will be renamed to this name\n"
        "Name can use mako template where obj is an "
        "ir_attachement. template exemple : "
        "  ${obj.name}-${obj.create_date}.csv",
    )
    after_import = fields.Selection(
        selection=[
            ("rename", "Rename"),
            ("move", "Move"),
            ("move_rename", "Move & Rename"),
            ("delete", "Delete"),
        ],
        help="Action after import a file",
    )
    file_type = fields.Selection(
        selection=[],
        string="File Type",
        help="The file type determines an import method to be used "
        "to parse and transform data before their import in ERP",
    )
    enabled = fields.Boolean("Enabled", default=True)
    check_duplicated_files = fields.Boolean(
        string="Check duplicated files",
        help="If checked, will avoid duplication file import",
    )
    emails = fields.Char(
        string="Notification Emails",
        help="List of email which should be notified in case of failure "
        "when excuting the files linked to this task",
    )

    def toogle_enabled(self):
        for task in self:
            task.enabled = not task.enabled

    def _prepare_attachment_vals(self, data, filename):
        self.ensure_one()
        vals = {
            "name": filename,
            "datas": data,
            "datas_fname": filename,
            "task_id": self.id,
            "file_type": self.file_type or False,
        }
        return vals

    @api.model
    def _template_render(self, template, record):
        try:
            template = mako_template_env.from_string(tools.ustr(template))
        except Exception:
            _logger.exception("Failed to load template %r", template)

        variables = {"obj": record}
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.exception(
                "Failed to render template %r using values %r" % (template, variables)
            )
            render_result = u""
        if render_result == u"False":
            render_result = u""
        return render_result

    @api.model
    def run_task_import_scheduler(self, domain=None):
        if domain is None:
            domain = []
        domain = expression.AND(
            [domain, [("method_type", "=", "import"), ("enabled", "=", True)]]
        )
        for task in self.search(domain):
            task.run_import()

    def run_import(self):
        self.ensure_one()
        attach_obj = self.env["attachment.queue"]
        backend = self.backend_id
        filepath = self.filepath or ""
        filenames = backend._list(relative_path=filepath, pattern=self.pattern)
        if self.check_duplicated_files:
            filenames = self._file_to_import(filenames)
        total_import = 0
        for file_name in filenames:
            with api.Environment.manage():
                with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    try:
                        full_absolute_path = os.path.join(filepath, file_name)
                        data = backend._get_b64_data(full_absolute_path)
                        attach_vals = self._prepare_attachment_vals(data, file_name)
                        attachment = attach_obj.with_env(new_env).create(attach_vals)
                        new_full_path = False
                        if self.after_import == "rename":
                            new_name = self._template_render(self.new_name, attachment)
                            new_full_path = os.path.join(filepath, new_name)
                        elif self.after_import == "move":
                            new_full_path = os.path.join(self.move_path, file_name)
                        elif self.after_import == "move_rename":
                            new_name = self._template_render(self.new_name, attachment)
                            new_full_path = os.path.join(self.move_path, new_name)
                        if new_full_path:
                            backend._add_b64_data(new_full_path, data)
                        if self.after_import in (
                            "delete",
                            "rename",
                            "move",
                            "move_rename",
                        ):
                            backend._delete(full_absolute_path)
                        total_import += 1
                    except Exception as e:
                        new_env.cr.rollback()
                        raise e
                    else:
                        new_env.cr.commit()
        _logger.info("Run import complete! Imported {0} files".format(total_import))

    def _file_to_import(self, filenames):
        imported = (
            self.env["attachment.queue"]
            .search([("name", "in", filenames)])
            .mapped("name")
        )
        return list(set(filenames) - set(imported))

    def button_toogle_enabled(self):
        for rec in self:
            rec.enabled = not rec.enabled

    def button_duplicate_record(self):
        self.ensure_one()
        record = self.copy({"enabled": False})
        return {
            "type": "ir.actions.act_window",
            "res_model": record.backend_id._name,
            "target": "current",
            "view_mode": "form",
            "res_id": record.backend_id.id,
        }
