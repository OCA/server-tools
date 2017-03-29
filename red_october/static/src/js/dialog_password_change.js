/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.DialogPasswordChange', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var mixins = require('red_october.mixins');
    var Model = require('web.DataModel');

    var _t = core._t;

    /* It allows a user to change their profile password.

        Attributes:
     */
    var DialogPasswordChange = Dialog.extend(
        mixins.dialogMixin,
        mixins.formMixin,
        {

            templateInner: 'red_october.FormPasswordChange',

            options: {
                title: _t('Change Encryption Password'),
                buttons: [
                    {
                        text: _t('Change Password'),
                        classes: 'btn btn-primary ro_btn_change_password',
                        click: function(event){
                            this.$form.submit();
                        },
                    },
                    {
                        text: _t('Cancel'),
                        classes: 'btn btn-default',
                        close: true,
                        click: function () {
                            this.resetUI();
                        }
                    },
                ],
            },

        }
    );

    return DialogPasswordChange;

});
