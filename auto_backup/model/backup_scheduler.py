#  -*- encoding: utf-8 -*-
##############################################################################
#     OpenERP, Open Source Management Solution
#     Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#     Copyright 2015 Agile Business Group <http://www.agilebg.com>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import xmlrpclib
import socket
import os
import time
import datetime
import base64
import re
try:
    import pysftp
except ImportError:
    raise ImportError(
        'This module needs pysftp to automaticly write backups to the FTP '
        'through SFTP.Please install pysftp on your system.'
        '(sudo pip install pysftp)'
    )
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from openerp import tools
from openerp import netsvc
import logging
_logger = logging.getLogger(__name__)


def execute(connector, method, *args):
    res = False
    try:
        res = getattr(connector, method)(*args)
    except socket.error as e:
        raise e
    return res


class db_backup(models.Model):
    _name = 'db.backup'

    def get_connection(self, host, port):
        uri = 'http://%s:%s' % (host, port)
        return xmlrpclib.ServerProxy(uri + '/xmlrpc/db')

    def get_db_list(self, host, port):
        conn = self.get_connection(host, port)
        db_list = execute(conn, 'list')
        return db_list

    @api.model
    def _get_db_name(self):
        return self.env.cr.dbname

    # Columns local server
    host = fields.Char(
        string='Host', default='localhost', size=100, required=True)
    port = fields.Char(
        string='Port', default='8069', size=10, required=True)
    name = fields.Char(
        string='Database', size=100, required=True,
        default=_get_db_name,
        help='Database you want to schedule backups for'
    )
    bkp_dir = fields.Char(
        string='Backup Directory', size=100,
        default='/odoo/backups',
        help='Absolute path for storing the backups',
        required=True
    )
    autoremove = fields.Boolean(
        string='Auto. Remove Backups',
        help=(
            "If you check this option you can choose to "
            "automaticly remove the backup after xx days"
        )
    )
    daystokeep = fields.Integer(
        string='Remove after x days',
        default=30,
        help=(
            "Choose after how many days the backup should be "
            "deleted. For example:\nIf you fill in 5 the backups "
            "will be removed after 5 days."
        ), required=True
    )
    sftpwrite = fields.Boolean(
        string='Write to external server with sftp',
        help=(
            "If you check this option you can specify the details "
            "needed to write to a remote server with SFTP."
        )
    )
    sftppath = fields.Char(
        string='Path external server',
        help=(
            "The location to the folder where the dumps should be "
            "written to. For example /odoo/backups/.\nFiles will then"
            " be written to /odoo/backups/ on your remote server."
        )
    )
    sftpip = fields.Char(
        string='IP Address SFTP Server',
        help=(
            "The IP address from your remote"
            " server. For example 192.168.0.1"
        )
    )
    sftpport = fields.Integer(
        string="SFTP Port",
        default=22,
        help="The port on the FTP server that accepts SSH/SFTP calls."
    )
    sftpusername = fields.Char(
        string='Username SFTP Server',
        help=(
            "The username where the SFTP connection "
            "should be made with. This is the user on the external server."
        )
    )
    sftppassword = fields.Char(
        string='Password User SFTP Server',
        help=(
            "The password from the user where the SFTP connection "
            "should be made with. This is the password from the user"
            " on the external server."
        )
    )
    daystokeepsftp = fields.Integer(
        string='Remove SFTP after x days',
        default=30,
        help=(
            "Choose after how many days the backup should be deleted "
            "from the FTP server. For example:\nIf you fill in 5 the "
            "backups will be removed after 5 days from the FTP server."
        )
    )
    sendmailsftpfail = fields.Boolean(
        string='Auto. E-mail on backup fail',
        help=(
            "If you check this option you can choose to automaticly"
            " get e-mailed when the backup to the external server failed."
        )
    )
    emailtonotify = fields.Char(
        string='E-mail to notify',
        help=(
            "Fill in the e-mail where you want to be"
            " notified that the backup failed on the FTP."
        )
    )
    lasterrorlog = fields.Text(
        string='E-mail to notify',
        help=(
            "Fill in the e-mail where you want to be"
            " notified that the backup failed on the FTP."
        )
    )

    @api.multi
    def _check_db_exist(self):
        for rec in self:
            db_list = self.get_db_list(rec.host, rec.port)
            if rec.name in db_list:
                return True
            return False

    _constraints = [
        (
            _check_db_exist,
            _('Error ! No such database exists!'), ['name']
        )
    ]

    @api.multi
    def test_sftp_connection(self):
        confs = self.search([])
        # Check if there is a success or fail and write messages
        messageTitle = ""
        messageContent = ""
        for rec in confs:
            # db_list = self.get_db_list(cr, uid, [], rec.host, rec.port)
            try:
                # pathToWriteTo = rec.sftppath
                ipHost = rec.sftpip
                portHost = rec.sftpport
                usernameLogin = rec.sftpusername
                passwordLogin = rec.sftppassword
                # Connect with external server over SFTP, so we know sure that
                # everything works.
                srv = pysftp.Connection(host=ipHost, username=usernameLogin,
                                        password=passwordLogin, port=portHost)
                srv.close()
                # We have a success.
                messageTitle = _("Connection Test Succeeded!")
                messageContent = _(
                    "Everything seems properly set up for FTP back-ups!")
            except Exception as e:
                messageTitle = _("Connection Test Failed!")
                if len(rec.sftpip) < 8:
                    messageContent += _(
                        "\nYour IP address seems to be too short.\n")
                messageContent += "Here is what we got instead:\n"
        if "Failed" in messageTitle:
            raise except_orm(
                _(messageTitle), _(
                    messageContent + "%s") %
                tools.ustr(e))
        else:
            raise Warning(_(messageTitle), _(messageContent))

    @api.model
    def schedule_backup(self):
        for rec in self.search([]):
            db_list = self.get_db_list(rec.host, rec.port)
            if rec.name in db_list:
                file_path = ''
                bkp_file = ''
                try:
                    if not os.path.isdir(rec.bkp_dir):
                        os.makedirs(rec.bkp_dir)
                except:
                    raise
                # Create name for dumpfile.
                bkp_file = '%s_%s.dimp.zip' % (
                    time.strftime('%d_%m_%Y_%H_%M_%S'),
                    rec.name)
                file_path = os.path.join(rec.bkp_dir, bkp_file)
                conn = self.get_connection(rec.host, rec.port)
                bkp = ''
                try:
                    bkp = execute(
                        conn, 'dump', tools.config['admin_passwd'], rec.name)
                except:
                    _logger.notifyChannel(
                        'backup', netsvc.LOG_INFO,
                        _(
                            "Couldn't backup database %s. "
                            "Bad database administrator"
                            "password for server running at http://%s:%s"
                        ) % (rec.name, rec.host, rec.port))
                    return False
                bkp = base64.decodestring(bkp)
                fp = open(file_path, 'wb')
                fp.write(bkp)
                fp.close()
            else:
                _logger.notifyChannel(
                    'backup', netsvc.LOG_INFO,
                    "database %s doesn't exist on http://%s:%s" %
                    (rec.name, rec.host, rec.port))
                return False
            # Check if user wants to write to SFTP or not.
            if rec.sftpwrite is True:
                try:
                    # Store all values in variables
                    dir = rec.bkp_dir
                    pathToWriteTo = rec.sftppath
                    ipHost = rec.sftpip
                    portHost = rec.sftpport
                    usernameLogin = rec.sftpusername
                    passwordLogin = rec.sftppassword
                    # Connect with external server over SFTP
                    srv = pysftp.Connection(
                        host=ipHost,
                        username=usernameLogin,
                        password=passwordLogin,
                        port=portHost)
                    # Move to the correct directory on external server. If the
                    # user made a typo in his path with multiple slashes
                    # (/odoo//backups/) it will be fixed by this regex.
                    pathToWriteTo = re.sub('([/]{2,5})+', '/', pathToWriteTo)
                    try:
                        srv.chdir(pathToWriteTo)
                    except IOError:
                        # Create directory and subdirs if they do not exist.
                        currentDir = ''
                        for dirElement in pathToWriteTo.split('/'):
                            currentDir += dirElement + '/'
                            try:
                                srv.chdir(currentDir)
                            except:
                                _logger.info(
                                    _(
                                        '(Part of the) path didn\'t exist. '
                                        'Creating it now at %s'
                                    ) % currentDir
                                )
                                # Make directory and then navigate into it
                                srv.mkdir(currentDir, mode=777)
                                srv.chdir(currentDir)
                                pass
                    srv.chdir(pathToWriteTo)
                    # Loop over all files in the directory.
                    for f in os.listdir(dir):
                        fullpath = os.path.join(dir, f)
                        if os.path.isfile(fullpath):
                            srv.put(fullpath)

                    # Navigate in to the correct folder.
                    srv.chdir(pathToWriteTo)

                    # Loop over all files in the directory from the back-ups.
                    # We will check the creation date of every back-up.
                    for file in srv.listdir(pathToWriteTo):
                        # Get the full path
                        fullpath = os.path.join(pathToWriteTo, file)
                        if srv.isfile(fullpath) and ".dump.zip" in file:
                            # Get the timestamp from the file on the external
                            # server
                            timestamp = srv.stat(fullpath).st_atime
                            createtime = (
                                datetime.datetime.fromtimestamp(timestamp)
                            )
                            now = datetime.datetime.now()
                            delta = now - createtime
                            # If the file is older than the daystokeepsftp (the
                            # days to keep that the user filled in on the Odoo
                            # form it will be removed.
                            if (
                                rec.daystokeepsftp > 0 and
                                delta.days >= rec.daystokeepsftp
                            ):
                                # Only delete files, no directories!
                                srv.unlink(file)
                    # Close the SFTP session.
                    srv.close()
                except Exception as e:
                    _logger.debug(
                        'Exception! We couldn\'t back '
                        'up to the FTP server..'
                    )
                    # At this point the SFTP backup failed.
                    # We will now check if the user wants
                    # an e-mail notification about this.
                    if rec.sendmailsftpfail:
                        try:
                            self.write({'lasterrorlog': tools.ustr(e)})
                            abk_template = self.env.ref(
                                'auto_backup.'
                                'email_template_autobackup_error_noificaiton',
                                False
                            )
                            abk_template.send_mail(self.id)
                        except Exception:
                            pass

            """Remove all old files (on local server) in case this is configured..
            This is done after the SFTP writing to prevent unusual behaviour:
            If the user would set local back-ups to be kept 0 days and the SFTP
            to keep backups xx days there wouldn't be any new back-ups added
            to the SFTP.
            If we'd remove the dump files before they're writen to the SFTP
            there willbe nothing to write. Meaning that if an user doesn't want
            to keep back-ups locally and only wants them on the SFTP
            (NAS for example) there wouldn't be any writing to the
            remote server if this if statement was before the SFTP write method
            right above this comment.
            """
            if rec.autoremove is True:
                dir = rec.bkp_dir
                # Loop over all files in the directory.
                for f in os.listdir(dir):
                    if os.path.isfile(fullpath) and ".dump.zip" in f:
                        fullpath = os.path.join(dir, f)
                        timestamp = os.stat(fullpath).st_ctime
                        createtime = (
                            datetime.datetime.fromtimestamp(timestamp)
                        )
                        now = datetime.datetime.now()
                        delta = now - createtime
                        if delta.days >= rec.daystokeep:
                            os.remove(fullpath)
        return True

#  vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
