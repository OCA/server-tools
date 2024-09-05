# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import datetime
import logging

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
    backend_id = fields.Many2one("fs.storage", string="Backend")
    attachment_ids = fields.One2many("attachment.queue", "task_id", string="Attachment")
    move_path = fields.Char(help="Imported File will be moved to this path")
    new_name = fields.Char(
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
            try:
                task.run_import()
            except Exception as e:
                self.env.cr.rollback()
                # log exception and continue in order to no block all task from all
                # remote servers one is unavailable
                _logger.warning(
                    "Task import %s failed with error %s" % (task.name, str(e))
                )

    def run(self):
        for record in self:
            method = "run_{}".format(record.method_type)
            if not hasattr(self, method):
                raise NotImplementedError
            else:
                getattr(record, method)()

    def _get_files(self):
        self.ensure_one()
        fs = self.backend_id.fs
        filepath = self.filepath or ""
        filepath = filepath.rstrip(fs.sep)
        if filepath and not fs.exists(filepath):
            return []
        if self.pattern:
            path = filepath and fs.sep.join([filepath, self.pattern]) or self.pattern
            file_path_names = fs.glob(path)
        else:
            file_path_names = fs.ls(filepath, detail=False)
        if self.avoid_duplicated_files:
            file_path_names = self._filter_duplicates(file_path_names)
        return file_path_names

    def _manage_file_after_import(self, file_name, fullpath, attachment):
        self.ensure_one()
        fs = self.backend_id.fs
        new_name = False
        if self.after_import == "rename":
            new_name = self._template_render(self.new_name, attachment)
            path = self.filepath or ""
        elif self.after_import == "move":
            new_name = file_name
            path = self.move_path or ""
        elif self.after_import == "move_rename":
            new_name = self._template_render(self.new_name, attachment)
            path = self.move_path or ""
        if new_name:
            new_full_path = fs.sep.join([path.rstrip(fs.sep), new_name])
            fs.move(fullpath, new_full_path)
        if self.after_import == "delete":
            fs.rm(fullpath)

    def run_import(self):
        self.ensure_one()
        attach_obj = self.env["attachment.queue"]
        file_path_names = self._get_files()
        total_import = 0
        fs = self.backend_id.fs
        for file_path in file_path_names:
            if fs.isdir(file_path):
                continue
            # we need to commit after each file because it may be renamed, deleted
            # moved on remote and if it fails later, we would could lose the file
            # forever.
            with self.env.registry.cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                file_name = file_path.split(fs.sep)[-1]
                data = base64.b64encode(fs.cat_file(file_path))
                attach_vals = self.with_env(new_env)._prepare_attachment_vals(
                    data, file_name
                )
                attachment = attach_obj.with_env(new_env).create(attach_vals)
                self.with_env(new_env)._manage_file_after_import(
                    file_name, file_path, attachment
                )
                total_import += 1
        _logger.info("Run import complete! Imported {} files".format(total_import))

    def _filter_duplicates(self, file_path_names):
        fs = self.backend_id.fs
        self.ensure_one()
        if self.filepath:
            filenames = [x.split(fs.sep)[-1] for x in file_path_names]
        else:
            filenames = file_path_names
        imported = (
            self.env["attachment.queue"]
            .search([("name", "in", filenames)])
            .mapped("name")
        )
        file_path_names_no_duplicate = [
            x for x in file_path_names if x.split(fs.sep)[-1] not in imported
        ]
        return file_path_names_no_duplicate

    def run_export(self):
        for task in self:
            for att in task.attachment_ids.filtered(lambda a: a.state == "pending"):
                att.run_as_job()

    def button_duplicate_record(self):
        # due to orm limitation method call from ui should not have params
        # so we need to define this method to be able to copy
        # if we do not do this the context will be injected in default params
        self.copy()

    def copy(self, default=None):
        if default is None:
            default = {}
        if "active" not in default:
            default["active"] = False
        return super().copy(default=default)
