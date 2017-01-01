/* Copyright 2016 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */

odoo.define('red_october.WidgetPassword', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Model = require('web.DataModel');

    WidgetChooseProfile = Widget.extend({

        template: 'red_october.WidgetGetPassword',

        init: function (parent) {
            this._super(parent);
            this.profiles = new Set();
            this.currentProfile = {};
        },

        start: function () {
            this._super();
            this.loadData();
        }

        loadData: function () {
            var RedOctoberUser = new Model('red.october.user');
            var self = this;
            RedOctoberUser.call('get_current_profile', []).then(function (profile) {
                self.loadProfile(profile, true);
            })
            RedOctoberUser.call('get_user_profiles', []).then(this.loadProfile);
            this.renderElement();
        },

        loadProfile: function (profile, current) {
            this.profiles.add(profile);
            if (current) {
                this.currentProfile = profile;
            }
        }

        renderElement: function () {
            this._super();
            if (this.profiles.length < 2) {
                this.$el.hide();
            } else {
                this.$el.show();
                this.$el.find('.ro-profile-select-item').click(self.selectProfile);
            }
        },

        selectProfile: function (event) {
            var profileID = $(event.currentTarget).data('profile-id');
            var self = this;
            if (profileID === self.currentProfileID) {
                return;
            }
            var uri = '/red_october/profile/change/' + profileID;
            return self.rpc(uri).done(function () {
                self.
            })
        },

    })

    return WidgetChooseProfile;

});
