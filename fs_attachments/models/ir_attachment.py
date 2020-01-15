# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import os
from odoo import api, fields, models, tools, SUPERUSER_ID, exceptions, _
from os import walk
import hashlib
import logging
from unicodedata import normalize
import string
from odoo.tools import config, human_size, ustr, html_escape

_logger = logging.getLogger(__name__)

FS_IDENT = 'filesystem://'

class IrModel(models.Model):
    _inherit = 'ir.model'

    # TODO: Issue a reload of the directories from the watcher thread
    filesystem_storage = fields.Boolean('Filesystem Storage', default=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    filesystem_storage_path = fields.Char('Filesystem Storage Path')
    uri_storage_path = fields.Char('URI for Storage Path')


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    filesystem_rel_file_path = fields.Char('Rel File path', index=True)

    @api.model
    def os_path_separators(self):
        seps = []
        for sep in os.path.sep, os.path.altsep:
            if sep:
                seps.append(sep)
        return seps

    @api.model
    def sanitise_filesystem_name(self, potential_file_path_name):
        '''
        Function borrowed from https://stackoverflow.com/questions/13939120/sanitizing-a-file-path-in-python/37095514
        Thanks to Tom Bull https://stackoverflow.com/users/2010738/tom-bull
        :param potential_file_path_name:
        :return:
        '''
        # Sort out unicode characters
        valid_filename = normalize('NFKD', potential_file_path_name).encode('ascii', 'ignore').decode('ascii')
        # Replace path separators with underscores
        for sep in self.os_path_separators():
            valid_filename = valid_filename.replace(sep, '_')
        # Ensure only valid characters
        valid_chars = "-_.() {0}{1}".format(string.ascii_letters, string.digits)
        valid_filename = "".join(ch for ch in valid_filename if ch in valid_chars)
        # Ensure at least one letter or number to ignore names such as '..'
        valid_chars = "{0}{1}".format(string.ascii_letters, string.digits)
        test_filename = "".join(ch for ch in potential_file_path_name if ch in valid_chars)
        if len(test_filename) == 0:
            # Replace empty file name or file path part with the following
            valid_filename = "(Empty Name)"
        return valid_filename

    @api.multi
    def _get_rel_filesystem_path(self, model_id):
        self.ensure_one()
        model_obj = self.env[model_id.model].sudo().with_context(lang=self.company_id.partner_id.lang)
        # First - check if the given model does provide a spezialised function to generate relative path
        if hasattr(model_obj, 'filesystem_storage_rel_path'):
            _logger.info("Do return stored path")
            return model_obj.browse(self.res_id).filesystem_storage_rel_path
        # Do use company language here for filename and path calculation
        record = model_obj.browse(self.res_id)
        return os.path.join(model_id.name, record.display_name)

    @api.model
    def _get_filesystem_path_parts(self, path):
        if path.startswith(FS_IDENT):
            # Get company id from path
            parts = path.split('/')
            company_id = parts[2]
            return (company_id, path[len(FS_IDENT)+len(company_id)+1::])

    @api.model
    def _full_path(self, path):
        if path.startswith(FS_IDENT):
            # Get company id from path
            (company_id, relpath) = self._get_filesystem_path_parts(path)
            company = self.env['res.company'].sudo().browse(int(company_id))
            return os.path.join(company.filesystem_storage_path, relpath)
        return super(IrAttachment, self)._full_path(path)

    @api.model
    def _file_delete(self, fname):
        if fname.startswith(FS_IDENT):
            file_path = self._full_path(fname)
            with tools.ignore(OSError):
                os.unlink(file_path)
            # Check for empty folder - remove empty folder
            with tools.ignore(OSError):
                dirpath = os.path.dirname(file_path)
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
        else:
            return super(IrAttachment, self)._file_delete(fname)

    def _inverse_datas_filesystem(self, model_id):
        for attach in self:
            # compute the fields that depend on datas
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            # Calculate filesystem storage path
            rel_path = attach._get_rel_filesystem_path(model_id)
            abs_path = attach.company_id.filesystem_storage_path
            complete_path = os.path.join(abs_path, rel_path)
            if attach.store_fname and attach.store_fname.startswith(FS_IDENT):
                # This attachment is already stored on filesystem - this is a update - so use old filename
                (company_id, rel_file_path) = self._get_filesystem_path_parts(attach.store_fname)
                file_path = os.path.join(attach.company_id.filesystem_storage_path, rel_file_path)
            else:
                filename = self.sanitise_filesystem_name(attach.datas_fname)
                rel_file_path = os.path.join(rel_path, filename)
                file_path = os.path.join(complete_path, filename)
                i = 1
                while(os.path.exists(file_path)):
                    filename = "(%s) - %s" % (i, filename)
                    rel_file_path = os.path.join(rel_path, filename)
                    file_path = os.path.join(complete_path, filename)
                    i += 1
            if not os.path.isdir(complete_path):
                os.makedirs(complete_path)
            with open(file_path, 'wb') as fp:
                fp.write(bin_data)
            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': attach.store_fname or "filesystem://%s/%s" % (attach.company_id.id, rel_file_path, ),
                'filesystem_rel_file_path': rel_file_path,
                'db_datas': False,
                'is_filesystem_storage': True,
            }
            # write as superuser, as user probably does not have write access
            super(IrAttachment, attach.sudo()).write(vals)

    def _inverse_datas(self):
        model_id = None
        if self.res_model and self.res_id:
            model_id = self.env['ir.model'].with_context(lang=self.company_id.partner_id.lang).search([('model', '=', self.res_model)])
        if model_id and model_id.filesystem_storage and self.company_id.filesystem_storage_path:
            return self._inverse_datas_filesystem(model_id)
        return super(IrAttachment, self)._inverse_datas()

    is_filesystem_storage = fields.Boolean('Stored on Filesystem', default=False)

    @api.model
    def resync_all_cron(self):
        '''
        Do load all companies with filesystem storage support
        Do load all models with filesystem storage support
        Do load all records with filesystem_rel_file_path set
        Call resync for every such record
        :return:
        '''
        for company in self.env['res.company'].sudo().search(
                [('filesystem_storage_path', '!=', False)]):
            _logger.info("Do work on company %s", company.display_name)
            for model_obj in self.env['ir.model'].sudo().with_context(lang=company.partner_id.lang).search([('filesystem_storage', '=', True)]):
                model = self.env[model_obj.model]
                _logger.info("Do work on model %s", model_obj.name)
                if hasattr(model, 'filesystem_storage_rel_path'):
                    records = model.search([('filesystem_storage_rel_path', '!=', False)])
                    for record in records:
                        self.resync(record, company=company)

    @api.model
    def resync(self, record, company=None):
        '''
        Do list files in my storage directory - and sync with ir.attachments in database
        :param res_model:
        :param res_ids:
        :return:
        '''
        if not company and hasattr(record, "company_id"):
            company = record.company_id
        if not company:
            _logger.error("No company given for resync - so we are not able to do something here...")
            return
        # First - check if the given model does provide a spezialised function to generate relative path
        if hasattr(record, 'filesystem_storage_rel_path'):
            _logger.info("Do return stored path")
            path = record.filesystem_storage_rel_path
        else:
            # Do use company language here for filename and path calculation
            path = os.path.join(record._model, record.display_name)
        abs_path = os.path.join(company.filesystem_storage_path, path)
        for (dirpath, dirnames, filenames) in walk(abs_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                rel_filepath = os.path.relpath(filepath, company.filesystem_storage_path)
                _logger.info("Search for attachment in %s", rel_filepath)
                attachment = self.search([('filesystem_rel_file_path', '=', rel_filepath), ('company_id', '=', company.id)])
                if not attachment:
                    _logger.info("Do create new attachment for file %s", filename)
                    self.filesystem_create_event(company_id=company.id, path=rel_filepath, fullpath=filepath, record=record)

    @api.model
    def filesystem_delete_event(self, company_id, path):
        '''
        File or directory in path got deleted on filesystem - sync changes here
        Search for existing ir.attachment - delete it
        :param path:
        :return:
        '''
        attachment = self.search([('filesystem_rel_file_path', '=', path), ('company_id', '=', company_id)])
        if attachment:
            attachment.with_context(filesystem_delete=True).unlink()

    @api.multi
    def _get_filesystem_record_by_path(self, path):
        for model_obj in self.env['ir.model'].sudo().with_context(lang=self.company_id.partner_id.lang).search([('filesystem_storage', '=', True)]):
            model = self.env[model_obj.model]
            if hasattr(model, 'filesystem_storage_rel_path'):
                paths = []
                curpath = ""
                for parts in os.path.split(os.path.dirname(path)):
                    newpath = os.path.join(curpath, parts)
                    paths.append(newpath)
                    _logger.info("Do add path %s", newpath)
                    curpath = newpath
                record = model.search([('filesystem_storage_rel_path', 'in', paths)])
                if record:
                    return record

    @api.model
    def filesystem_create_event(self, company_id, path, fullpath, record=None):
        '''
        File or directory in path got created on filesystem - sync changes here
        Search for existing ir.attachment in the same rel file path - so we get the res_model and res_id
        Create new ir.attachment if found
        :param path:
        :return:
        '''
        # Check for existing attachment
        attachment = self.search(
            [('filesystem_rel_file_path', '=', path), ('company_id', '=', company_id)], limit=1)
        if attachment:
            _logger.info("ir.attachment for %s does already exists" % path)
            return
        only_path = os.path.dirname(path)
        # Get record if not specified
        if not record:
            record = self._get_filesystem_record_by_path(path)
        attachment = None
        if not record:
            attachment = self.search(
                [('filesystem_rel_file_path', 'like', '%s%%' % only_path), ('company_id', '=', company_id)], limit=1)
        if attachment or record:
            # Read file binary
            with open(fullpath, 'rb') as f:
                bin_data = f.read()
            checksum = hashlib.sha1(bin_data or b'').hexdigest()
            # Check mimetype
            mimetype = self._compute_mimetype({
                'datas_fname': os.path.basename(path),
            })
            # Create attachment
            new_attachment = self.with_context(filesystem_create=True).create({
                'name': os.path.basename(path),
                'checksum': checksum,
                'type': 'binary',
                'bin_size': human_size(os.path.getsize(fullpath)),
                'company_id': company_id,
                'res_model': record._name if record else attachment.res_model,
                'res_id': record.id if record else attachment.res_id,
                'is_filesystem_storage': True,
                'filesystem_rel_file_path': path,
                'store_fname': "filesystem://%s/%s" % (company_id, path, ),
                'db_datas': False,
                'datas_fname': os.path.basename(path),
                'index_content': self._index(bin_data, os.path.basename(path), mimetype),
                'mimetype': mimetype,
            })
            _logger.info("Created new attachment %s", new_attachment)
