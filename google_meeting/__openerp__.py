# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Solutions2use (<http://www.solutions2use.com>)
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
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
    'name': 'Google Meeting',
    'author': 'solutions2use',
    'website': "http://www.solutions2use.com",
    'license': 'AGPL-3',
    'version': "1.0",
    "depends": [
        'base_calendar'
    ],
    'description': """
Odoo solution for synchronizing crm_meeting with Google Calendar

Installation notes
------------------
Before you are able running this module you must install google api client
for python :

https://developers.google.com/api-client-library/python/start/installation
Now install the google_meeting module in your Odoo 7.0 system. If any errors
occur this has to do with the needed dependencies the module need (apiclient,
httplib2, oauth2client, uritemplate, argparse).

In **Settings->Users->Users** enable **Google API / Manager**
in **Access Rights** for those users having admin rights.
Enable **Google API / User** for those users you want to have synchronisation
enabled for there calendars.

Setup a google account for using google api:

https://code.google.com/apis/console/
Follow the instructions by Google to create such an account if you haven’t got
one yet. In the console create a new project. Give it a name (for example: API
Project). Go to the **Services** section of your created project and switch
**calendar API** to **on**.

Now go to the **API settings** section of your project and click on **Create
another client ID …** and select **Installed application** as Application type.
Select **other** as Installed application type (this option will be visible
after selecting the correct Application type).
Now click on **Create client ID**.

Now you have a **Client ID for installed applications** with a Client ID,
Client secret, Redirect URIs. On the right you see a button **Download JSON**.
Click on this button and save this file on a location where your Odoo system
has access to it (read/write).

In Odoo login as admin, you have a menu **Google API**. Create an account for
accessing your google API. Go to **Google API ->Configuration->Accounts**.
Click on the create button ,give your account a name.

In **Secrets path** enter the full path of your json file you just have
downloaded (i.g: /srv/odoo/google_calendar/client_secrets.json).
In **Credential path** enter a full path (filename included) where
google_meeting will find/create the credential file
(i.g: /srv/odoo/google_calendar/credentials.dat). The first time this
credentials file does not exists.

When you’re done save your account, the button **Authorize** becomes red.
To test if everything is correct, click on this button.

It's important that you have your browser opened on the same machine as
Odoo-Server is running.

If everything goes well a new page opens in your browser, asking to accept
that the Odoo module google_meeting wants to manage your calendars and to view
your calendars (if not visible you have to login first). Click the accept
button. Now the credential file is created.

If you have problems using this method deactivate **Use local browser** in
**Google Api->Configuration->Accounts->[your account]**, stop your Odoo-Server
and run it in interactive mode.

After clicking the **Authorize** button in your terminal you see a link.
Copy this link and paste it in a browser on a device where this is possible.
Here you will receive a code, enter this code in your terminal where the system
is waiting for it. Stop Odoo-Server and start it again the way you always do.

The last thing you have to do is to create calendars in your account you want
to sync with Odoo. For each user you want to have this option you must create
one calendar. See http://www.google.com/calendar to create your calendars.
Don’t forget to share this calendar with the user for whom this calendar is.
This user also must have a google account.

In the calendar settings you have a private address with a little xml button.
Click on it and copy the link into an text editor. The link looks like:

https://www.google.com/calendar/feeds/
ghzfw33qcgtoahz1hq7cdsj321%40group.calendar.google.com/
private-35403bc2f4aad7ce56b21a976516b21/basic

Now copy the string between **feeds/** and **/private**, you have something
likethis:

ghzfw33qcgtoahz1hq7cdsj321%40group.calendar.google.com

Replace **%40** with the **@** sign, resulted in the following Google Calendar
id:

ghzfw33qcgtoahz1hq7cdsj321@group.calendar.google.com

Go back to Odoo and create a calendar **Google Api->Configuration->Calendars**.
Here you must select the account you just have created, the user this calendar
belongs to and the **Google calendar id**.

Save your data and click the button **Synchronize** to test it.
In **Messaging->Organizer->Calendar** you can see if events were
created/changed and/or deleted.

The module google_meeting synchronizes every 15 minutes. You can change this in
**Settings->Technical->Scheduler**.

You also have the possibility you use the notifications option of google,
in this case google triggers some link you must define.
In this trigger you can call the do_synchronize method of the
google_meeting module.

Contributors
------------

* Alex Comba <alex.comba@agilebg.com>
""",
    'category': 'Google Apps',
    'data': [
        'data/scheduler.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'view/google_api_account_view.xml',
        'view/google_api_calendar_view.xml',
        'view/menu_view.xml',
    ],
    'external_dependencies': {
        'python': ['google-api-python-client'],
    },
    'demo': [],
    'test': [],
    'installable': True,

}
