# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Database Auto-Backup",
    "version" : "1.0",
    "author" : "VanRoey.be - Yenthe Van Ginneken",
    "website" : "http://www.vanroey.be/applications/bedrijfsbeheer/odoo",
    "category" : "Generic Modules",
    "summary": "Backups",
    "description": """The Database Auto-Backup module enables the user to make configurations for the automatic backup of the database. Backups can be taken on the local system or on a remote server, through SFTP.
You only have to specify the hostname, port, backup location and databasename (all will be pre-filled by default with correct data.
If you want to write to an external server with SFTP you will need to provide the IP, username and password for the remote backups.
The base of this module is taken from Odoo SA V6.1 (https://www.odoo.com/apps/modules/6.0/auto_backup/) and then upgraded and heavily expanded.
This module is made and provided by VanRoey.be.

Automatic backup for all such configured databases can then be scheduled as follows:  
                      
1) Go to Settings / Technical / Automation / Scheduled actions.
2) Search the action 'Backup scheduler'.
3) Set it active and choose how often you wish to take backups.
4) If you want to write backups to a remote location you should fill in the SFTP details.
""",
    "depends" : ['base'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["bkp_conf_view.xml","backup_data.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
