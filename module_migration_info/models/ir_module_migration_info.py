# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class IrModuleMigration(models.Model):
    _name = "ir.module.migration.info"

    module_id = fields.Many2one("ir.module.module")
    module_name = fields.Char(string="Module Name")
    mig_version = fields.Char(string="Version")

    mig_title = fields.Char(string="Title")
    mig_url = fields.Char(string="URL")
    # mig_state = fields.Selection([("open", "Open"), ("merged", "Merged")], string="State")
    mig_status = fields.Char(string="State")
    mig_opened = fields.Char(string="Opened")
    mig_merged = fields.Char(string="Merged")
    mig_no_of_reviewers = fields.Char(string="No of reviewers")
    mig_no_of_comments = fields.Char(string="No of comments")