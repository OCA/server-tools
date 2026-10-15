# 2019  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def _index(self, *args, **kwargs):
        return False

    def _fetch_query(self, query, fields):
        """Give ``index_content`` the content of the file when the database has none.

        The content is not stored, so the column is empty, but whoever reads the field
        still needs its value: core reads it to look a color up in the CSS bundle of the
        website. Read it from the file, as the indexation would have stored it, and only
        put it in the cache: nothing is written to the database.
        """
        fetched = super()._fetch_query(query, fields)
        field = self._fields["index_content"]
        if fetched and field in fields:
            cache = field._get_cache(self.env)
            for attachment in fetched:
                if cache.get(attachment.id):
                    continue
                content = self._index_content_from_file(attachment)
                if content:
                    field._update_cache(attachment, content)
        return fetched

    def _index_content_from_file(self, attachment):
        """Return what the indexation would have stored for ``attachment``."""
        raw = attachment.raw
        if not raw:
            return False
        # Skip this class: it is the one that disables the indexation
        return super()._index(raw, attachment.mimetype, checksum=attachment.checksum)
