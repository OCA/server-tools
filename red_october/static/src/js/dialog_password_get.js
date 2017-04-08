/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.DialogPasswordGet', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var mixins = require('red_october.mixins');
    var Model = require('web.DataModel');

    var _t = core._t;

    /* It allows a user to get their profile password.

        Attributes:
     */
    var DialogPasswordGet = Dialog.extend(
        mixins.dialogMixin,
        mixins.formMixin,
        {

            templateInner: 'red_october.FormPasswordGet',

            options: {
                title: _t('Enter Encryption Password'),
                buttons: [
                    {
                        text: _t('Submit'),
                        classes: 'btn btn-primary ro_btn_get_password',
                        close: true,
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

            handleSubmit: function(event) {
                event.preventDefault();
                var $target = $(event.target);
                var password = $target.find('.form-control').val()
                this.getParent().currentPassword = password;
            },

        }
    );

    return DialogPasswordGet;

});
