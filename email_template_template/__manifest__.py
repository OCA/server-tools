# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    "name": "Templates for email templates",
    "version": "1.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "category": 'Tools',
    'complexity': "expert",
    "description": """If an organisation's email layout is a bit more
complicated, changes can be tedious when having to do that across several email
templates. So this addon allows to define templates for mails that is referenced
by other mail templates.
This way we can put the layout parts into the template template and only content
in the other templates. Changing the layout is then only a matter of changing
the template template.

-----
Usage
-----
Create an email template with the related document model 'Email Templates'. Now
most of the fields gray out and you can only edit body_text and body_html. Be
sure to use ${body_text} and ${body_html} respectively in your template
template.

Then select this newly created template templates in one of your actual
templates.

For example, create a template template

::

   Example Corp logo
   Example Corp header
   ${object.body_text} <- this gets evaluated to the body_text of a template using this template template
   Example Corp
   Example street 42
   Example city
   Example Corp footer

Then in your template you write

::

   Dear ${object.partner_id.name},

   Your order has been booked on date ${object.date} for a total amount of ${object.sum}.

And it will be evaluated to

::

    Example Corp logo
    Example Corp header
    Dear Jane Doe,

    Your order has been booked on date 04/17/2013 for a total amount of 42.
    Example Corp
    Example street 42
    Example city
    Example Corp footer

Given the way evaluation works internally (body_text of the template template
is evaluated two times, first with the instance of email.template of your own
template, then with the object your template refers to), you can do some
trickery if you know that a template template is always used with the same
kind of model (that is, models that have the same field name):

In your template template:

::

    Dear ${'${object.name}'}, <-- gets evaluated to "${object.name}" in the
    first step, then to the content of object.name
    ${object.body_html}
    Best,
    Example Corp
""",
    'website': 'https://github.com/OCA/server-tools',
    'images': [],
    'depends': ['email_template'],
    'data': [
        'view/email_template.xml',
    ],
    "license": 'AGPL-3',
    'installable': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
