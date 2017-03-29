/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.mixins', function (require) {
    "use strict";

    var core = require('web.core');

    var QWeb = core.qweb;

    /* It should provide a more basic version of website_form js.
     * This allows for removal of website dependencies.
     */
    var formMixin = {

        handleSubmit: function(event) {
            event.preventDefault();
            var $target = $(event.target);
            var data = $target.serializeArray();
            return $.ajax({
                method: $target.attr('method') || 'GET',
                url: $target.attr('action'),
                data: data,
                dataType: 'json',
            }).done($.proxy(this.handleResponse, this));
        },

        handleResponse: function (data) {
            if (!data) {
                data = {'errors': ['An unknown error occured.']};
            }
            if(data.errors.length) {
                this.handleResponseFail(data);
            } else {
                this.handleResponseSuccess(data);
            }
        },

        handleResponseSuccess: function(data) {
            this.resetUI();
            if (this.$modal) {
                this.$modal.hide();
            }
            var redirectUri = this.$target.data('success-page');
            if (redirectUri) {
                window.location.href = redirectUri;
            }
        },

        handleResponseFail: function (data) {
            var $errorDivs = $('<div />');
            _.each(data.errors, function(error) {
                $errorDivs.append(
                    $('<div class="alert bg-danger">' + error + '</div>')
                );
            });
            this.$form.find('.form_result').html($errorDivs);
        },

        handleInputKeypress: function(event) {
            if (event.which == 13) {  // If enter key
                $(event.target).parents('form').submit();
            }
        },

        start: function () {
            var $target = this.$target || this.$el;
            if (!$target || !$target.submit) {
                return;
            }
            this.$form = $target;
            $target.submit($.proxy(this.handleSubmit, this));
            $target.find('input').keypress($.proxy(this.handleInputKeypress, this))
            this._super();
        },

        resetUI: function () {
            this.$form.trigger('reset');
            this.$form.find('.form_result').html('');
        }

    };

    /* It provides a mixin for slightly more opionionated Dialogs.
     */
    var dialogMixin = {

        templateInner: undefined,
        roProfile: undefined,

        init: function(parent) {
            if (parent.currentProfile) {
                this.roProfile = parent.currentProfile;
            }
            if (this.templateInner) {
                this.$extraContent = $(
                    QWeb.render(
                        this.templateInner,
                        this.getTemplateContext()
                    )
                );
                if (this.options.$content) {
                    this.options.$content.insertAfter(this.$extraContent);
                } else {
                    this.options.$content = this.$extraContent;
                }
            }
            this._super(parent, this.options);
        },

        getTemplateContext: function() {
            return {
                csrf_token: core.csrf_token,
                profile: this.roProfile,
            }
        },

    };

    return {
        dialogMixin: dialogMixin,
        formMixin: formMixin,
    };

});
