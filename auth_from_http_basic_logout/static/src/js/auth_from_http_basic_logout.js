//-*- coding: utf-8 -*-
//############################################################################
//
//   OpenERP, Open Source Management Solution
//   This module copyright (C) 2014 Therp BV (<http://therp.nl>).
//
//   This program is free software: you can redistribute it and/or modify
//   it under the terms of the GNU Affero General Public License as
//   published by the Free Software Foundation, either version 3 of the
//   License, or (at your option) any later version.
//
//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU Affero General Public License for more details.
//
//   You should have received a copy of the GNU Affero General Public License
//   along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//############################################################################

openerp.auth_from_http_basic_logout = function(openerp)
{
    openerp.web.Session.include({
        session_logout: function()
        {
            var deferred = this._super(this, arguments);
            deferred.fail(function(error, ev)
            {
                ev.preventDefault();
                openerp.web.blockUI();
                jQuery('.openerp_webclient_container').remove();
                jQuery('.oe_blockui_spin_container')
                    .empty()
                    .html(
                        _.string.sprintf(
                            openerp.web._t(
                                '<p style="background: white">You have been logged out successfully. <a href="#">Click here to log in again.</a></p>')
                            ))
                    .click(function() 
                    {
                        window.location.reload();
                    });
            });
            return deferred;
        }
    });
}
