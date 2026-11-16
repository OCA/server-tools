from odoo import fields, models


class IssueAutoSendLog(models.Model):
    _name = "issue.auto.send.log"
    _description = "Error Report Log"
    _order = "last_date desc, id desc"
    _rec_name = "title"
    _company_digest_index = models.Index("(company_id, digest)")

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        ondelete="cascade",
    )
    digest = fields.Char(
        required=True,
        help="Hash of the traceback; the same error always gets the same hash.",
    )
    module = fields.Char(help="Odoo module that raised the error.")
    title = fields.Char()
    url = fields.Char(
        string="Report URL",
        help="GitHub issue or file created for the last report of this error.",
    )
    occurrence_count = fields.Integer(
        string="Occurrences",
        default=1,
        help="How often the error occurred, including the skipped duplicates.",
    )
    first_date = fields.Datetime(
        string="First Occurrence",
        default=fields.Datetime.now,
    )
    last_date = fields.Datetime(
        string="Last Occurrence",
        default=fields.Datetime.now,
    )
    last_sent_date = fields.Datetime(
        string="Last Reported",
        help="When the error was last sent to GitHub or by email. Empty if sending "
        "failed.",
    )
