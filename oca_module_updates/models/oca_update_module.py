# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

import feedparser
from packaging.version import Version

from odoo import _, api, fields, models


class OcaUpdateModule(models.Model):

    _name = "oca.update.module"
    _description = "Oca Update Module"  # TODO
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    version_id = fields.Many2one(
        "oca.update.version", required=True, string="Main version"
    )
    tag_ids = fields.Many2many("oca.update.tag")
    last_version = fields.Char(readonly=True)
    last_update = fields.Datetime(readonly=True, default="2000-01-01")
    published_on = fields.Datetime(readonly=True)
    url = fields.Char(compute="_compute_url")

    @api.depends("name", "last_version")
    def _compute_url(self):
        for record in self:
            record.url = record.last_version and "https://pypi.org/project/%s/%s" % (
                record._get_pypi_code(),
                record.last_version,
            )

    def _get_pypi_code(self):
        header = "odoo"
        if self.version_id.old_system:
            header += self.version_id.name
        return "%s-addon-%s" % (header, self.name.replace("_", "-"))

    def feed_data(self):
        self.ensure_one()
        current_version = False
        if self.last_version:
            current_version = Version(self.last_version)
        feed = feedparser.parse(
            "https://pypi.org/rss/project/%s/releases.xml" % self._get_pypi_code()
        )
        last_entry = None
        for entry in feed.entries:
            version = Version(entry["title"])
            if (not current_version or version >= current_version) and str(
                version.major
            ) == self.version_id.name:
                current_version = version
                last_entry = entry
        if current_version and (
            not self.last_version or current_version > Version(self.last_version)
        ):
            self._publish_version(str(current_version), entry=last_entry)
            return True
        if not current_version and self.last_version:
            self._publish_version(False)
            return True
        self.last_update = fields.Datetime.now()
        return False

    def _publish_version(self, version, entry):
        self.write(
            {
                "last_version": version,
                "last_update": fields.Datetime.now(),
                "published_on": datetime.strptime(
                    entry["published"], "%a, %d %b %Y %H:%M:%S %Z"
                )
                if entry
                else False,
            }
        )
        self.message_post(
            body=_("New version %s published") % version,
            message_type="notification",
        )
        return True

    def cron_update(self, with_commit=True, limit=100):
        for record in self.search([], order="last_update ASC", limit=limit):
            record.feed_data()
            if with_commit:
                self.env.cr.commit()  # pylint: disable=E8102
        return True
