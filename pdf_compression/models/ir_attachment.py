# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
import os
import re
import subprocess
from distutils.version import LooseVersion
from tempfile import NamedTemporaryFile

from openerp import api, models
from openerp.tools.misc import find_in_path


_logger = logging.getLogger(__name__)


def _get_ghostscript_bin():
    ghostscript_bin = find_in_path('ghostscript')
    if ghostscript_bin is None:
        raise IOError
    return ghostscript_bin

# Check the presence of Ghostscript and return its version at Odoo start-up

ghostscript_state = 'install'
try:
    process = subprocess.Popen(
        [_get_ghostscript_bin(), '--version'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
except (OSError, IOError):
    _logger.info('You need Ghostscript to compress pdfs.')
else:
    _logger.info('Will use the Ghostscript binary at %s' %
                 _get_ghostscript_bin())
    out, err = process.communicate()
    version = re.search('([0-9.]+)', out).group(0)
    if LooseVersion(version) < LooseVersion('9.18'):
        _logger.info('Upgrade Ghostscript to (at least) 9.18')
        ghostscript_state = 'upgrade'
    else:
        _logger.info('Ghostscript version ' + version)
        ghostscript_state = 'ok'


class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    @api.model
    def create(self, values):
        if 'mimetype' not in values:
            values['mimetype'] = self._compute_mimetype(values)
        if values.get('mimetype') == 'application/pdf' and values.get(
                'datas'):
            try:
                values['datas'] = self._run_ghostscript(values['datas'])
            except (OSError, IOError, ValueError):
                _logger.warning('You need Ghostscript to compress pdfs.')

        return super(IrAttachment, self).create(values)

    @api.multi
    def write(self, values):
        if 'mimetype' not in values:
            values['mimetype'] = self._compute_mimetype(values)
        if values.get('mimetype') == 'application/pdf' and values.get(
                'datas'):
            try:
                values['datas'] = self._run_ghostscript(values['datas'])
            except (OSError, IOError, ValueError):
                _logger.warning('You need Ghostscript to compress pdfs.')

        return super(IrAttachment, self).write(values)

    @api.model
    def _run_ghostscript(self, pdf):
        ir_values = self.env['ir.values']
        compression = ir_values.get_default('ir.attachment', 'compression')
        pdfa_option = ir_values.get_default('ir.attachment', 'pdfa_option')
        report_override = self._context.get('pdf_option')

        if pdfa_option != 'no' or report_override != 'default' or \
                compression != 'no':

            command_args = []
            local_command_args = []

            with NamedTemporaryFile(delete=False, suffix='.pdf') as f1:
                f1.write(base64.decodestring(pdf))

            f2 = NamedTemporaryFile(delete=False, suffix='.pdf')
            f2.close()

            input_file = f1.name
            output_file = f2.name

            if pdfa_option != 'no' and (report_override == 'default' or
                                        not report_override):
                if pdfa_option == 'pdfa1b':
                    local_command_args.extend([
                        '-dPDFA=1',
                        '-dProcessColorModel=/DeviceRGB',
                        '-dColorConversionStrategy=/RGB',
                    ])
                elif pdfa_option == 'pdfa2b':
                    local_command_args.extend([
                        '-dPDFA=2',
                        '-dProcessColorModel=/DeviceRGB',
                        '-dColorConversionStrategy=/RGB',
                        '-dEmbedAllFonts=true',
                        '-dMaxSubsetPct=100',
                        '-dSubsetFonts=true'
                    ])

            if report_override != 'default':
                if report_override == 'pdfa1b':
                    local_command_args.extend([
                        '-dPDFA=1',
                        '-dProcessColorModel=/DeviceRGB',
                        '-dColorConversionStrategy=/RGB',
                    ])
                elif report_override == 'pdfa2b':
                    local_command_args.extend([
                        '-dPDFA=2',
                        '-dProcessColorModel=/DeviceRGB',
                        '-dColorConversionStrategy=/RGB',
                        '-dEmbedAllFonts=true',
                        '-dMaxSubsetPct=100',
                        '-dSubsetFonts=true'])

            if compression == 'no' and (pdfa_option == 'pdfa1b' or
                                        report_override == 'pdfa1b'):
                local_command_args.extend(['-dPDFSETTINGS=/default'])
            elif compression == 'prepress':
                local_command_args.extend(['-dPDFSETTINGS=/prepress'])
            elif compression == 'screen':
                local_command_args.extend(['-dPDFSETTINGS=/screen'])
            elif compression == 'ebook':
                local_command_args.extend(['-dPDFSETTINGS=/ebook'])
            elif compression == 'printer':
                local_command_args.extend(['-dPDFSETTINGS=/printer'])
            elif compression == 'default':
                local_command_args.extend(['-dPDFSETTINGS=/default'])

            local_command_args.extend(
                ['-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                 '-dNOPAUSE', '-dQUIET', '-dBATCH', '-dNOOUTERSAVE',
                 '-sOutputFile=' + output_file, input_file])

            try:
                ghostscript = [_get_ghostscript_bin()] + command_args + \
                    local_command_args
                process = subprocess.Popen(ghostscript, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                out, err = process.communicate()

                if err:
                    _logger.info('ghostscript failed . Message: %s' % err)

                with open(output_file, 'rb') as f3:
                    pdf = base64.encodestring(f3.read())

                os.unlink(input_file)
                os.unlink(output_file)

            except (OSError, IOError, ValueError):
                raise

        return pdf
