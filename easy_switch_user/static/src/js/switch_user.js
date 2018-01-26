odoo.define('easy_switch_user', function(require) {
    var Widget = require('web.Widget');
    var SystrayMenu = require('web.SystrayMenu');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    var _t = core._t;

    var SwitchUserMenu = Widget.extend({
        template: 'SwitchUserMenu',
        events: {
            'click .dropdown-menu li a[data-user-login]': 'user_selected'
        },
        start: function() {
            var res = this._super.apply(this, arguments);
            this.loadUsers().then(this.populate.bind(this));
            return res;
        },
        loadUsers: function() {
            return this._rpc({
                model: 'res.users',
                method: 'search_read',
                order: 'name asc'
            });
        },
        populate: function(users) {
            var self = this;
            var stored = this.get_stored_passwords();
            var users_stored = [];
            var users_not_stored = [];
            for(var i in users)
                if(users[i].login in stored)
                    users_stored.push(users[i]);
                else
                    users_not_stored.push(users[i]);

            this.$('.dropdown-menu').html('');
            this.populate_users(users_stored);
            if(users_stored.length > 0)
                this.$('.dropdown-menu').append('<li class="divider"></li>');
            this.populate_users(users_not_stored);
        },
        populate_users: function(users) {
            var self = this;
            _.each(users, function(user) {
                var inside = session.uid == user.id ?
                    '<b>' + user.name + ' (' + user.login + ')</b>' :
                    user.name + ' (' + user.login + ')';
                self.$('.dropdown-menu').append(
                    '<li><a href="#" data-user-login="' + user.login + '">' + inside + '</a></li>'
                )
            });
        },
        get_stored_passwords: function() {
            var val = sessionStorage.getItem('easy_switch_user');
            if (!val) return {};
            return JSON.parse(val);
        },
        store_password: function(login, password) {
            var store = {};
            var val = sessionStorage.getItem('easy_switch_user');
            if (val) store = JSON.parse(val);
            store[login] = password;
            sessionStorage.setItem('easy_switch_user', JSON.stringify(store));
        },
        user_selected: function(e) {
            var self = this;
            var user_login = $(e.currentTarget).attr('data-user-login');
            var passwords = this.get_stored_passwords();
            if (user_login in passwords) {
                this.switch_user(user_login, passwords[user_login]);
            } else {
                var dialog = new SwitchUserLoginDialog(this, user_login);
                dialog.on('login', this, function(password) {
                    dialog.hideError();
                    self.switch_user(user_login, password, true).fail(function() {
                        dialog.showError();
                    });
                });
                dialog.open();
            }
        },
        switch_user: function(login, password, store=false) {
            var self = this;
            return ajax.jsonRpc('/easy_switch_user/switch', 'call', {
                login: login,
                password: password
            }).then(function() {
                if(store)
                    self.store_password(login, password);
                window.location.reload();
            });
        }
    });

    SystrayMenu.Items.push(SwitchUserMenu);

    var SwitchUserLoginDialog = Dialog.extend({
        login: $.Deferred(),
        init: function(parent, user_login) {
            this._super(parent, {
                title: _t('Switch User'),
                $content: $(qweb.render('SwitchUserLoginDialog', {'login': user_login})),
                buttons: [
                    { text: _t("Login"), classes: 'btn-primary', click: this.login },
                    { text: _t("Cancel"), close: true }
                ]
            });
        },
        login: function() {
            this.trigger('login', this.$('input[type="password"]').val());
        },
        showError: function() {
            this.$('.alert-danger').removeClass('hidden');
        },
        hideError: function() {
            this.$('.alert-danger').addClass('hidden');
        }
    });

    return {
        Menu: SwitchUserMenu,
        Dialog: SwitchUserLoginDialog
    };
});
