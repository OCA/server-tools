# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api
from openerp.exceptions import AccessError
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.addons.web.http import request
from openerp.addons.report.models.report import _get_wkhtmltopdf_bin

import base64
import logging
import tempfile
import os
import subprocess
from contextlib import closing

_logger = logging.getLogger(__name__)


class Report(osv.Model):
    _inherit = "report"

    @api.v8
    def get_pdf(self, records, report_name, html=None, data=None):
        """This method generates and returns pdf version of a report.
        """
        ctx = dict(self._context)
        report = self._get_report_from_name(report_name)
        ctx.update({'pdf_option': report.pdf_option})
        return super(Report, self.with_context(ctx)).get_pdf(
            records, report_name, html=html, data=data)

    @api.v7
    def get_pdf(self, cr, uid, ids, report_name, html=None, data=None,
                context=None):
        """override to add pdf_option to the context"""
        ctx = dict(context)
        report = self._get_report_from_name(cr, uid, report_name)
        ctx.update({'pdf_option': report.pdf_option})
        return super(Report, self).get_pdf(
            cr, uid, ids, report_name, html=html, data=data, context=context)

    def _run_wkhtmltopdf(self, cr, uid, headers, footers, bodies, landscape,
                         paperformat, spec_paperformat_args=None,
                         save_in_attachment=None, context=None):
        """Execute wkhtmltopdf as a subprocess in order to convert html given
        in input into a pdf document.

        :param header: list of string containing the headers
        :param footer: list of string containing the footers
        :param bodies: list of string containing the reports
        :param landscape: boolean to force the pdf to be rendered under a
        landscape format
        :param paperformat: ir.actions.report.paperformat to generate the
        wkhtmltopf arguments
        :param specific_paperformat_args: dict of prioritized
        paperformat arguments
        :param save_in_attachment: dict of reports to save/load in/from the db
        :returns: Content of the pdf as a string
        """
        command_args = []

        # Passing the cookie to wkhtmltopdf in order to resolve internal links.
        try:
            if request:
                command_args.extend(
                    ['--cookie', 'session_id', request.session.sid])
        except AttributeError:
            pass

        # Wkhtmltopdf arguments
        command_args.extend(['--quiet'])  # Less verbose error messages
        if paperformat:
            # Convert the paperformat record into arguments
            command_args.extend(
                self._build_wkhtmltopdf_args(
                    paperformat, spec_paperformat_args))

        # Force the landscape orientation if necessary
        if landscape and '--orientation' in command_args:
            command_args_copy = list(command_args)
            for index, elem in enumerate(command_args_copy):
                if elem == '--orientation':
                    del command_args[index]
                    del command_args[index]
                    command_args.extend(['--orientation', 'landscape'])
        elif landscape and '--orientation' not in command_args:
            command_args.extend(['--orientation', 'landscape'])

        # Execute WKhtmltopdf
        pdfdocuments = []
        temporary_files = []

        for index, reporthtml in enumerate(bodies):
            local_command_args = []
            pdfreport_fd, pdfreport_path = tempfile.mkstemp(
                suffix='.pdf', prefix='report.tmp.')
            temporary_files.append(pdfreport_path)

            # Directly load the document if we already have it
            if save_in_attachment and save_in_attachment[
                    'loaded_documents'].get(reporthtml[0]):
                with closing(os.fdopen(pdfreport_fd, 'w')) as pdfreport:
                    pdfreport.write(
                        save_in_attachment['loaded_documents'][reporthtml[0]])
                pdfdocuments.append(pdfreport_path)
                continue
            else:
                os.close(pdfreport_fd)

            # Wkhtmltopdf handles header/footer as separate pages.
            # Create them if necessary.
            if headers:
                head_file_fd, head_file_path = tempfile.mkstemp(
                    suffix='.html', prefix='report.header.tmp.')
                temporary_files.append(head_file_path)
                with closing(os.fdopen(head_file_fd, 'w')) as head_file:
                    head_file.write(headers[index])
                local_command_args.extend(['--header-html', head_file_path])
            if footers:
                foot_file_fd, foot_file_path = tempfile.mkstemp(
                    suffix='.html', prefix='report.footer.tmp.')
                temporary_files.append(foot_file_path)
                with closing(os.fdopen(foot_file_fd, 'w')) as foot_file:
                    foot_file.write(footers[index])
                local_command_args.extend(['--footer-html', foot_file_path])

            # Body stuff
            content_file_fd, content_file_path = tempfile.mkstemp(
                suffix='.html', prefix='report.body.tmp.')
            temporary_files.append(content_file_path)
            with closing(os.fdopen(content_file_fd, 'w')) as content_file:
                content_file.write(reporthtml[1])

            try:
                wkhtmltopdf = [_get_wkhtmltopdf_bin()] + command_args + \
                    local_command_args
                wkhtmltopdf += [content_file_path] + [pdfreport_path]

                process = subprocess.Popen(wkhtmltopdf, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                out, err = process.communicate()

                if process.returncode not in [0, 1]:
                    raise osv.except_osv(_('Report (PDF)'),
                                         _('Wkhtmltopdf failed ('
                                           'error code: %s). '
                                           'Message: %s') % (
                                         str(process.returncode), err))

                # Save the pdf in attachment if marked
                if reporthtml[0] is not False and save_in_attachment.get(
                        reporthtml[0]):
                    with open(pdfreport_path, 'rb') as pdfreport:
                        attachment = {
                            'name': save_in_attachment.get(reporthtml[0]),
                            'datas': base64.encodestring(pdfreport.read()),
                            'datas_fname': save_in_attachment.get(
                                reporthtml[0]),
                            'res_model': save_in_attachment.get('model'),
                            'res_id': reporthtml[0], }
                        try:

                            #################
                            # Bloopark change
                            #################

                            self.pool['ir.attachment'].create(
                                cr, uid, attachment, context=context)
                        except AccessError:
                            _logger.warning("Cannot save PDF report %r as "
                                            "attachment",
                                            attachment['name'])
                        else:
                            _logger.info(
                                'The PDF document %s is now saved in the '
                                'database',
                                attachment['name'])

                pdfdocuments.append(pdfreport_path)
            except:
                raise

        # Return the entire document
        if len(pdfdocuments) == 1:
            entire_report_path = pdfdocuments[0]
        else:
            entire_report_path = self._merge_pdf(pdfdocuments)
            temporary_files.append(entire_report_path)

        with open(entire_report_path, 'rb') as pdfdocument:
            content = pdfdocument.read()

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error(
                    'Error when trying to remove file %s' % temporary_file)

        return content
