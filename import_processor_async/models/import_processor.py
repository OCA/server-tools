# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from uuid import uuid4

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ImportProcessor(models.Model):
    _inherit = "import.processor"

    async_processing = fields.Boolean(
        default=False,
        help="Enabling this will disable the post processing and passing of the "
        "context from the pre-processor",
    )
    channel_id = fields.Many2one("queue.job.channel")

    def process_entry(self, process_uuid, entry, localdict, **kwargs):
        # Reset the pre-defined values
        if not self.async_processing:
            self._process_entry(process_uuid, entry, localdict, **kwargs)
            return

        self.with_delay(
            description="Processing",
            channel=self.channel_id.complete_name or "root",
            identity_key=f"import/{process_uuid}/{uuid4()}",
        )._process_entry(process_uuid, entry, {}, **kwargs)

    def _post_process(self, process_uuid, localdict):
        if not self.async_processing:
            return super()._post_process(process_uuid, localdict)
