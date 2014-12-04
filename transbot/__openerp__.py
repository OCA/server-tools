# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Odoo Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Translations bot',
    'version': '1.0',
    'category': 'Website',
    'description': """
This module enables a bot that checks selected Github branches and dump
.pot and .po files to a given Transifex account, and detects translations done
on Transifex and dump back on Github.

Installation
============

This module requires two external libraries:

* txlib to handle Transifex API available at
https://github.com/transifex/transifex-python-library
* pygithub for Github API that can be downloaded using *pip install PyGithub*.

Configuration
=============

* In Transbot > Configuration

Transifex
---------

* Configure a user and a password for Transifex. This cannot be done via
a token, because Transifex doesn't allow this option. This data is stored
as system parameters, so password is going to be in plain text, although
in the configuration screen appears masked. 
* Make sure to create a password authenticated user and not a oauth
authenticated user (Linkedin, Github, Facebook).
* Configure a Transifex organization and team. Team is identified by a slug
or name, derived from the real name you have put. The translation group is
an id (number) that can be seen in the URL when you are on it on the web page.
* The Transifex translation group must have added the corresponding languages
that can be synchronized with Github, or you will get an error on contrary.

Github
------

* You have to issue a new token for the user you want to interact with on
Github, with all the permissions granted, and put on the corresponding field
on the configuration.
* Last, you have to create a Github project record for each of the repos,
putting the organization of the repo and the project name in it. There is no
support for now for personal repos, only organization repos, but it's very
easy to create an organization for you only.

Transbot
--------

* Create a Github project and click on Get branches to retrieve current
branches. You can deactivate any branch you don't want in the list 
(for example, dev branches).
* Then, you can click on Check Github updates to query active branches of
the current Transbot project for new files, creating a Transifex project for
each branch with this convention: <project_name> (<branch_name>), and
uploading pot and po files. Here there can be errors that are logged 
(for example, an empty translation file like fr_BE.po in vertical-hotel).
* After this, you can click also on Check Transifex updates, which detects
possible changes on translation strings on Transifex, and dump back on Github.
This is awfully slow, but there's no other way, because it has to download
each set of translation strings and check against saved hash, because
Transifex doesn't provide any other method.
* There are 2 crons that can be changed for automatic check of both sides.

Known issues
============

* If you check Transifex updates before Github, it will be produce
  an inconsistent behaviour or even an error.
* Not all communications exceptions with APIs are caught and registered
  on log for now, so you can have that cron process halts silently, so please
  check Odoo log frequently.
    """,
    'author': 'Serv. Tecnolog. Avanzados - Pedro M. Baeza',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python': ['github', 'txlib'],
    },
    'data': [
        'data/ir_cron.xml',
        'views/transbot_menus.xml',
        'views/transbot_project_view.xml',
        'views/transbot_log_view.xml',
        'views/res_config_view.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
}
