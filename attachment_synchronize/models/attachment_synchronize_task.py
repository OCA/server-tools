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
        [("import", "Import Task"), ("export", "Export Task")], required=True
    )
    pattern = fields.Char(
        string="Selection Pattern",
        help="Pattern used to select the files to be imported following the 'fnmatch' "
        "special characters (e.g. '*.txt' to catch all the text files).\n"
        "If empty, import all the files found in 'File Path'.",
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
        help="Imported File will be renamed to this name.\n"
        "New Name can use 'mako' template where 'obj' is the original file's name.\n"
        "For instance : ${obj.name}-${obj.create_date}.csv",
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
        help="Used to fill the 'File Type' field in the imported 'Attachments Queues'."
        "\nFurther operations will be realized on these Attachments Queues depending "
        "on their 'File Type' value.",
    )
    active = fields.Boolean("Enabled", default=True)
    avoid_duplicated_files = fields.Boolean(
        string="Avoid importing duplicated files",
        help="If checked, a file will not be imported if an Attachment Queue with the "
        "same name already exists.",
    )
    failure_emails = fields.Char(
        string="Failure Emails",
        help="Used to fill the 'Failure Emails' field in the 'Attachments Queues' "
        "related to this task.\nAn alert will be sent to these emails if any operation "
        "on these Attachment Queue's file type fails.",
    )
    count_attachment_failed = fields.Integer(compute="_compute_count_state")
    count_attachment_pending = fields.Integer(compute="_compute_count_state")
    count_attachment_done = fields.Integer(compute="_compute_count_state")

    def _compute_count_state(self):
        for record in self:
            for state in ["failed", "pending", "done"]:
                record["count_attachment_{}".format(state)] = len(
                    record.attachment_ids.filtered(lambda r: r.state == state)
                )

    def _prepare_attachment_vals(self, data, filename):
        self.ensure_one()
        vals = {
            "name": filename,
            "datas": data,
            "task_id": self.id,
            "file_type": self.file_type or False,
        }
        return vals

    @api.model
    def _template_render(self, template, record):
        try:
            template = mako_template_env.from_string(tools.ustr(template))
        except Exception:
            _logger.exception("Failed to load template '{}'".format(template))

        variables = {"obj": record}
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.exception(
                "Failed to render template '{}'' using values '{}'".format(
                    template, variables
                )
            )
            render_result = ""
        if render_result == "False":
            render_result = ""
        return render_result

    @api.model
    def run_task_import_scheduler(self, domain=None):
        if domain is None:
            domain = []
        domain = expression.AND([domain, [("method_type", "=", "import")]])
        for task in self.search(domain):
            task.run_import()

    def run(self):
        for record in self:
            method = "run_{}".format(record.method_type)
            if not hasattr(self, method):
                raise NotImplementedError
            else:
                getattr(record, method)()

    def run_import(self):
        self.ensure_one()
        attach_obj = self.env["attachment.queue"]
        backend = self.backend_id
        filepath = self.filepath or ""
        filenames = backend._list(relative_path=filepath, pattern=self.pattern)
        if self.avoid_duplicated_files:
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
        _logger.info("Run import complete! Imported {} files".format(total_import))

    def _file_to_import(self, filenames):
        imported = (
            self.env["attachment.queue"]
            .search([("name", "in", filenames)])
            .mapped("name")
        )
        return list(set(filenames) - set(imported))

    def run_export(self):
        for task in self:
            task.attachment_ids.filtered(lambda a: a.state == "pending").run()

    def button_duplicate_record(self):
        # due to orm limitation method call from ui should not have params
        # so we need to define this method to be able to copy
        # if we do not do this the context will be injected in default params
        # in V14 maybe we can call copy directly
        self.copy()

    def copy(self, default=None):
        if default is None:
            default = {}
        if "active" not in default:
            default["active"] = False
        return super().copy(default=default)
