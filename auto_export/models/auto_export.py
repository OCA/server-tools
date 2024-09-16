# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import datetime
import logging
import os

import pytz

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import normalize_domain
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AutoExport(models.Model):
    _name = "auto.export"
    _inherit = ["mail.thread"]
    _description = "Automated Export Template"
    _order = "name asc, ir_model_id asc"

    @api.model
    def _get_default_user_id(self):
        return self.env.user

    @api.model
    def _get_saving_protocol_selection(self):
        return [
            ("filesystem", "Filesystem"),
        ]

    name = fields.Char(string="Name", required=True,)
    user_id = fields.Many2one(
        string="User",
        help="The export job will be triggered using the selected user's "
        "access rights. It means that the export result may differ "
        "depending on the user's groups.",
        comodel_name="res.users",
        required=True,
        ondelete="restrict",
        default=lambda self: self._get_default_user_id(),
        tracking=True,
        index=True,
    )
    ir_model_id = fields.Many2one(
        string="Data model",
        help="Odoo model corresponding to the data to export (e.g. Invoices).",
        comodel_name="ir.model",
        required=True,
        ondelete="restrict",
        domain=[("transient", "=", False)],
        tracking=True,
        index=True,
    )
    ir_export_id = fields.Many2one(
        string="Saved export",
        help="Saved export from the standard Odoo export tool to use to "
        "select the columns (fields) to export.",
        comodel_name="ir.exports",
        required=True,
        ondelete="restrict",
        tracking=True,
        index=True,
    )
    technical_domain = fields.Char(
        string="Technical domain",
        help="Optional Odoo domain to filter on the rows to export "
        "(e.g. [('state', '=', 'open')]).",
        tracking=True,
    )
    filename_prefix = fields.Char(
        string="Filename prefix", required=True, tracking=True,
    )
    file_extension = fields.Selection(
        string="File format",
        selection=[(".csv", "CSV")],
        required=True,
        default=".csv",
    )
    saving_protocol = fields.Selection(
        string="Saving protocol",
        help="The Filesystem protocol means that the export file will be "
        "saved to a selected path of the filesystem.",
        selection=_get_saving_protocol_selection,
        default="filesystem",
        required=True,
        index=True,
    )
    filesystem_path = fields.Char(
        string="Filesystem path",
        help="Valid path on the filesystem where to save the export file.",
        tracking=True,
    )
    preview_recordset_count = fields.Integer(
        string="Number of records to export",
        compute="_compute_preview_recordset_count",
        store=False,
        readonly=True,
    )
    checkpoint_count = fields.Integer(
        string="Number of checkpoints",
        compute="_compute_checkpoints",
        store=False,
        readonly=True,
    )
    has_checkpoint = fields.Boolean(
        string="Has checkpoint(s)",
        compute="_compute_checkpoints",
        store=False,
        readonly=True,
        search="_search_has_checkpoint",
    )

    @api.onchange("ir_model_id")
    def _onchange_ir_model_id(self):
        self.ensure_one()
        self.ir_export_id = False
        return {"domain": {"ir_export_id": [("resource", "=", self.ir_model_id.model)]}}

    @api.onchange("saving_protocol")
    def _onchange_saving_protocol(self):
        self.ensure_one()
        if self.saving_protocol != "filesystem":
            self.filesystem_path = False

    @api.constrains("technical_domain")
    def _check_technical_domain(self):
        """
        This method tries to prevent the user from saving a domain with an
        invalid syntax.
        :raise: ValidationError
        """
        for rec in self:
            try:
                normalize_domain(rec._get_domain(raise_if_exception=True))
            except Exception:
                err_msg = _("Syntax error in the domain.")
                _logger.exception(err_msg)
                raise ValidationError(err_msg)

    @api.constrains("ir_model_id")
    def _check_ir_model_id(self):
        if any(rec.ir_model_id.transient for rec in self):
            raise ValidationError(_("Transient models cannot be exported."))

    @api.constrains("ir_export_id", "ir_model_id")
    def _check_ir_export_id(self):
        if any(rec.ir_export_id.resource != rec.ir_model_id.model for rec in self):
            raise ValidationError(
                _("The saved export does not match the selected data model.")
            )

    @api.constrains("filesystem_path", "saving_protocol")
    def _check_filesystem_path(self):
        if any(
            rec.saving_protocol == "filesystem" and not rec.filesystem_path
            for rec in self
        ):
            raise ValidationError(
                _(
                    "A valid path must be specified when 'Filesystem' is selected "
                    "as saving protocol."
                )
            )

    def _get_domain(self, raise_if_exception=False):
        """
        This method transforms the string domain into a valid list domain.
        :param raise_if_exception: True if any catch exception must be raised.
        It should not be enabled in a compute method.
        :return: list of tuples (domain)
        """
        self.ensure_one()
        # Catch any exception in interactive mode since it could prevent
        # the form opening
        is_async = "job_uuid" in self.env.context
        raise_if_exception = raise_if_exception or is_async
        try:
            return safe_eval(self.technical_domain) if self.technical_domain else []
        # pylint:disable=broad-except
        except Exception:
            if raise_if_exception:
                raise
            _logger.exception("Error in domain evaluation")

    def _get_secured_model(self):
        """
        This method prepares the model ready to be used as the specified user.
        :return: class with the right sudo()
        """
        self.ensure_one()
        if not self.ir_model_id:
            return False
        return self.env[self.ir_model_id.model].with_user(self.user_id)

    @api.depends("ir_model_id", "technical_domain", "user_id")
    def _compute_preview_recordset_count(self):
        """
        This method computes the preview_recordset_count field. It's the number
        of records that will be exported, depending on the specified user and
        domain. Zero can mean that the domain is invalid because all exceptions
        are catch and logged.
        """
        for rec in self:
            domain = rec._get_domain()
            model = rec._get_secured_model()
            # Catch all exceptions since a wrong model would block the UI
            try:
                rec.preview_recordset_count = model.search_count(domain)
            # pylint:disable=broad-except
            except Exception:
                _logger.exception("Computation error")
                rec.preview_recordset_count = 0

    def _compute_checkpoints(self):
        """
        This method computes the checkpoint_count and has_checkpoint fields.
        checkpoint_count is the number of checkpoints for each record and
        has_checkpoint defines whether the record has at least one checkpoint.
        """
        model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)
        res = self.env["connector.checkpoint"].read_group(
            domain=[
                ("model_id", "=", model.id),
                ("record_id", "in", self.ids),
                ("state", "=", "need_review"),
            ],
            fields=["record_id"],
            groupby=["record_id"],
        )
        checkpoint_dict = {}
        for dic in res:
            rec_id = dic["record_id"]
            checkpoint_dict.setdefault(rec_id, 0)
            checkpoint_dict[rec_id] += dic["record_id_count"]
        for rec in self:
            checkpoint_count = checkpoint_dict.get(rec.id, 0)
            rec.checkpoint_count = checkpoint_count
            rec.has_checkpoint = checkpoint_count > 0

    def _search_has_checkpoint(self, operator, value):
        model = self.env["ir.model"].search([("model", "=", self._name)])
        # Search for all records that need review for the current model
        records = self.env["connector.checkpoint"].search(
            [("model_id", "=", model.id), ("state", "=", "need_review")]
        )
        if records:
            domain = [("id", "in", records.mapped("record_id"))]
        else:
            domain = [("id", "=", 0)]
        value = bool(value)
        if (operator, value) in (("=", False), ("!=", True)):
            domain.insert(0, "!")
        return domain

    def preview_recordset(self):
        self.ensure_one()
        # The preview list may not be relevant for other users than Admin
        # since they would be restricted by ACLs and record rules
        # We do not allow access to the list if the records count is <= 0
        # because it could mean the domain is incorrect
        if self.env.user.id != SUPERUSER_ID or self.preview_recordset_count <= 0:
            return {}
        return {
            "name": _("Records to export"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": self.ir_model_id.model,
            "domain": self._get_domain(),
        }

    def _check_can_export(self):
        """
        This method checks whether the auto.export is ready to trigger
        the asynchronous export.
        :raise: UserError if something is wrong
        """
        self.ensure_one()
        if self.saving_protocol == "filesystem" and not os.path.exists(
            self.filesystem_path
        ):
            raise UserError(
                _(
                    "The specified path ({path}) does not exist. "
                    "Please set an existing path and trigger the export "
                    "again."
                ).format(path=self.filesystem_path)
            )

    def _prepare_full_filename(self):
        self.ensure_one()
        local_tz = pytz.timezone(self.env.user.tz or pytz.utc)
        local_datetime = pytz.utc.localize(datetime.datetime.now()).astimezone(local_tz)
        timestamp = local_datetime.strftime("%Y%m%d_%H%M%S_%f")
        filename = self.filename_prefix + "_" + timestamp + self.file_extension
        if self.saving_protocol == "filesystem":
            return os.path.join(self.filesystem_path, filename)
        return filename

    @api.model
    def _save_filesystem_csv(self, csv_rows, full_filename):
        """
        This method writes the data in the CSV file and saves it on the
        filesystem.
        :param csv_rows: list of lists (rows)
        :param full_filename: path + filename
        """
        with open(full_filename, "w+") as export_file:
            writer = csv.writer(export_file)
            writer.writerows([[s for s in row] for row in csv_rows])

    def _get_data_to_export(self):
        """
        This method creates and return the data to export.
        :return: tuple like: (fields list, rows list)
        """
        self.ensure_one()
        secured_model = self._get_secured_model()
        objects_export = secured_model.search(self._get_domain(raise_if_exception=True))
        field_names = self.ir_export_id.export_fields.mapped("name")
        export_data = objects_export.export_data(field_names).get("datas", [])
        return field_names, export_data

    def _export_data(self):
        """
        This method exports the data and saves it following the selected
        saving protocol and file format.
        """
        self.ensure_one()
        self._check_can_export()
        field_names, export_data = self._get_data_to_export()
        full_filename = self._prepare_full_filename()
        if self.file_extension == ".csv":
            csv_rows = [field_names]
            csv_rows.extend(export_data)
            if self.saving_protocol == "filesystem":
                self._save_filesystem_csv(csv_rows, full_filename)
        return full_filename

    def trigger_export(self):
        description = _(u"Asynchronous auto export: {auto_export_name}")
        for rec in self:
            rec.with_delay(
                description=description.format(auto_export_name=rec.display_name)
            )._do_trigger_export(rec.id)

    @api.model
    def _do_trigger_export(self, auto_export_id):
        auto_export_rec = self.env["auto.export"].browse(auto_export_id)
        # Log action
        message = _("Auto Export triggered")
        self.env["auto.export.backend"].get_backend().log_auto_export_action(
            msg=message, record=auto_export_rec, log_level="info"
        )
        # pylint:disable=broad-except
        try:
            full_filename = auto_export_rec._export_data()
            # Log success
            message = _("Auto Export: file {filename} created").format(
                filename=full_filename
            )
            self.env["auto.export.backend"].get_backend().log_auto_export_action(
                msg=message, record=auto_export_rec, log_level="info"
            )
        except Exception as e:
            self.env["auto.export.backend"].get_backend().process_auto_export_exception(
                record=auto_export_rec, e=e
            )
