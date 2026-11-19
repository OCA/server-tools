# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections.abc import Iterable

from odoo import api, fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    deduplicate_docs = fields.Boolean(
        string="Deduplicate Documents",
        help="If checked, the report will print only one copy of each document",
    )

    @api.model
    def _deduplicate_document_ids(
        self,
        report_ref: models.BaseModel | int | str,
        doc_ids: Iterable[api.IdType] | api.IdType | None,
    ) -> Iterable[api.IdType] | api.IdType | None:
        """Removes duplicates from ``document_ids`` if required by the report

        :param report_ref: the report to check for deduplication feature; can be any of
            - ir.actions.report record
            - ir.actions.report id
            - ir.model.data reference to ir.actions.report
            - ir.actions.report report_name
        :param doc_ids: the IDs to deduplicate; can be any of
            - iterable of IDs
            - single ID
            - None
        :returns: a list of deduplicated IDs if the original ``doc_ids`` is a
            non-empty iterable and the report requires document deduplication;
            else, returns ``doc_ids`` as-is
        """
        if (
            isinstance(doc_ids, Iterable)
            and doc_ids
            and self._get_report(report_ref).deduplicate_docs
        ):
            new_ids = []
            for doc_id in doc_ids:
                if doc_id not in new_ids:
                    new_ids.append(doc_id)
            return new_ids
        return doc_ids

    # --------------------------------------------------------------------------------#
    # OVERRIDES OF RENDERING METHODS                                                  #
    #                                                                                 #
    # Warning: these overrides may be incomplete.                                     #
    # In a perfect world, method ``_render()`` would be the common entry point for    #
    # all report rendering operations, with that method dispatching to                #
    # ``_render_*()`` according to the report type.                                   #
    # Unfortunately, that's not the case: there's plenty of code that directly calls  #
    # methods ``_render_*()`` bypassing ``_render()``, so we need to override those   #
    # methods too, and that makes it harder to keep track of all methods that require #
    # overriding.                                                                     #
    # There are also cases of ``_pre_render_qweb_pdf()`` being called directly, but   #
    # we don't override it because it always dispatches to ``_render_qweb_html()``    #
    # or ``_render_qweb_pdf_prepare_streams()`` (unless some strange overrides that   #
    # don't call ``super()`` are in place).                                           #
    # --------------------------------------------------------------------------------#

    @api.model
    def _render(self, report_ref, res_ids, data=None):
        res_ids = self._deduplicate_document_ids(report_ref, res_ids)
        return super()._render(report_ref, res_ids, data)

    @api.model
    def _render_qweb_html(self, report_ref, docids, data=None):
        docids = self._deduplicate_document_ids(report_ref, docids)
        return super()._render_qweb_html(report_ref, docids, data)

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        res_ids = self._deduplicate_document_ids(report_ref, res_ids)
        return super()._render_qweb_pdf(report_ref, res_ids, data)

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        res_ids = self._deduplicate_document_ids(report_ref, res_ids)
        return super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids)

    @api.model
    def _render_qweb_text(self, report_ref, docids, data=None):
        docids = self._deduplicate_document_ids(report_ref, docids)
        return super()._render_qweb_text(report_ref, docids, data)
