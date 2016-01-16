//-*- coding: utf-8 -*-
//© 2016 Therp BV <http://therp.nl>
//License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

openerp.base_encrypted_field = function(instance)
{
    instance.base_encrypted_field.get_pgp_keys = function(widget)
    {
        if(!widget.session.user_pgp_private_key)
        {
            return new instance.web.DataSet(widget, 'res.users')
            .read_ids([widget.session.uid], ['pgp_private_key', 'pgp_public_key'])
            .then(function(values)
            {
                values = values[0];
                if(values.pgp_private_key && values.pgp_public_key)
                {
                    var private_key = openpgp.key.readArmored(
                            values.pgp_private_key),
                        public_key = openpgp.key.readArmored(
                            values.pgp_public_key);
                    if(private_key.err || public_key.err)
                    {
                        throw new SyntaxError(
                            instance.web._t('Your keypair is invalid. Please regenerate it via your user settings')
                        )
                    }
                    widget.session.user_pgp_private_key = private_key.keys[0];
                    widget.session.user_pgp_public_key = public_key.keys[0];
                    return instance.base_encrypted_field.get_pgp_keys(widget);
                }
                else
                {
                    return instance.base_encrypted_field.update_pgp_keys(widget, widget.session.uid)
                    .then(function()
                    {
                        return instance.base_encrypted_field.get_pgp_keys(widget);
                    })
                }
            })
        }
        else
        {
            var deferred = new jQuery.Deferred();
            if(!widget.session.user_pgp_private_key.getEncryptionKeyPacket().isDecrypted)
            {
                widget.rpc(
                    '/web/action/load',
                    {action_id: 'base_encrypted_field.action_base_encrypted_field_get_passphrase'})
                .done(function(action)
                {
                    on_close = function()
                    {
                        if(!widget.session.user_pgp_private_key.getEncryptionKeyPacket().isDecrypted)
                        {
                            deferred.reject();
                        }
                    }
                    widget.do_action(action, {on_close: on_close}).then(function()
                    {
                        widget.field_manager.ViewManager.ActionManager.dialog_widget.dataset.on(
                            'dataset_changed', self, function(data)
                            {
                                if(data.passphrase)
                                {
                                    widget.session.user_pgp_private_key.decrypt(data.passphrase);
                                    if(!widget.session.user_pgp_private_key.getEncryptionKeyPacket().isDecrypted)
                                    {
                                        deferred.reject()
                                    }
                                    else
                                    {
                                        deferred.resolve(widget.session.user_pgp_private_key, widget.session.user_pgp_public_key);
                                    }
                                }
                            });
                    });
                })
            }
            else
            {
                deferred.resolve(widget.session.user_pgp_private_key, widget.session.user_pgp_public_key);
            }
            return deferred.promise();
        }
    }
    instance.base_encrypted_field.update_pgp_keys = function(widget, user_id)
    {
        if(!widget)
        {
            // we're call on a user form, find it and assign widget, user_id
            var find_pgp_widget = function(widget, form)
            {
                if(widget.field_manager && widget.field_manager.dataset &&
                   widget.field_manager.dataset.model == 'res.users' &&
                   widget.name == 'pgp_private_key')
                {
                    return widget;
                }
                if(widget.getChildren)
                {
                    var children = widget.getChildren();
                    for(var i=0; i < children.length; i += 1)
                    {
                        var found = find_pgp_widget(children[i], form);
                        if(found && found != form)
                        {
                            return found;
                        }
                    }
                }
                return form;
            }
            widget = find_pgp_widget(instance.webclient);
            user_id = widget.field_manager.dataset.ids[widget.field_manager.dataset.index];
        }
        return widget.rpc(
            '/web/action/load',
            {action_id: 'base_encrypted_field.action_base_encrypted_field_update_key'})
        .done(function(action)
        {
            var create_key_deferred = new jQuery.Deferred(),
            on_close = function()
            {
                if(widget.session.user_pgp_private_key)
                {
                    create_key_deferred.resolve(
                        widget.session.user_pgp_private_key,
                        widget.session.user_pgp_public_key);
                }
            }
            action.context = {}
            action.context.default_user_id = user_id;
            widget.do_action(action, {on_close: on_close}).then(function()
            {
                var res_users = new instance.web.DataSet(widget, 'res.users');
                widget.field_manager.ViewManager.ActionManager.dialog_widget.dataset.on(
                    'dataset_changed', self, function(data)
                    {
                        //TODO: save old keypair to recode afterwards
                        if(data.passphrase && !data.private_key)
                        {
                            return res_users.read_ids([data.user_id], ['name', 'email'])
                            .then(function(values)
                            {
                                values = values[0];
                                var options = {
                                    numBits: 4096,
                                    userId: _.str.sprintf('%s <%s>', values.name, values.email),
                                    passphrase: data.passphrase,
                                };
                                instance.web.blockUI();
                                return openpgp.generateKeyPair(options)
                                .then(function(keypair)
                                {
                                    widget.session.user_pgp_private_key = keypair.key;
                                    widget.session.user_pgp_public_key = keypair.key.toPublic();
                                    widget.session.user_pgp_private_key.decrypt(data.passphrase);
                                    create_key_deferred.resolve(
                                        widget.session.user_pgp_private_key,
                                        widget.session.user_pgp_public_key);
                                    return res_users.write(
                                        data.user_id,
                                        {
                                            pgp_public_key: keypair.publicKeyArmored,
                                            pgp_private_key: keypair.privateKeyArmored,
                                        })
                                    .then(function()
                                    {
                                        instance.web.unblockUI();
                                    });
                                });
                            })
                        }
                        else if(data.private_key)
                        {
                            if(data.passphrase && !data.public_key)
                            {
                                var private_key = openpgp.key.readArmored(
                                    data.private_key)
                                if(private_key.err)
                                {
                                    throw new SyntaxError(
                                        instance.web._t('Your private key is invalid'));
                                }
                                private_key = private_key.keys[0]
                                private_key.decrypt(data.passphrase);
                                if(!private_key.getEncryptionKeyPacket().isDecrypted)
                                {
                                    throw new SyntaxError(
                                        instance.web._t('Your passphrase is invalid'));
                                }
                                data.public_key = private_key.toPublic().armor();
                            }
                            if(data.user_id == widget.session.uid)
                            {
                                var private_key = openpgp.key.readArmored(
                                    data.private_key),
                                    public_key = openpgp.key.readArmored(
                                        data.public_key);
                                if(private_key.err || public_key.err)
                                {
                                    throw new SyntaxError(
                                        instance.web._t('Your keypair is invalid'));
                                }
                                widget.session.user_pgp_private_key = private_key.keys[0];
                                widget.session.user_pgp_public_key = public_key.keys[0];
                                if(data.passphrase)
                                {
                                    widget.session.user_pgp_private_key.decrypt(data.passphrase);
                                }
                            }
                            return res_users.write(
                                data.user_id,
                                {
                                    pgp_public_key: data.public_key,
                                    pgp_private_key: data.private_key,
                                });
                        }
                    });
            });
            return create_key_deferred.promise();
        })
    }
    instance.web.FormView.include({
        init: function()
        {
            this.encryptable_fields = {}
            return this._super.apply(this, arguments);
        },
        register_field: function(field, name)
        {
            if(field.field.encryptable)
            {
                this.encryptable_fields[name] = field;
            }
            return this._super.apply(this, arguments);
        },
        is_field_encryptable: function(field)
        {
            return this.encryptable_fields[field.name];
        },
        is_field_encrypted: function(field)
        {
            return false;
        },
    });
    instance.web.form.AbstractField.include({
        renderElement: function()
        {
            var result = this._super.apply(this, arguments),
                $containers = this.$el.add(this.$label);
            if(this.field_manager.is_field_encryptable &&
                this.field_manager.is_field_encryptable(this))
            {
                if(this.field_manager.is_field_encrypted(this))
                {
                    this.$el.addClass('oe_form_field_encrypted');
                    $containers.$label.find('.oe_field_decrypt').click(
                        this.proxy('on_decrypt'));
                    $containers.find('.oe_field_encrypt').remove();
                }
                else
                {
                    $containers.find('.oe_field_encrypt').click(
                        this.proxy('on_encrypt'));
                    $containers.find('.oe_field_decrypt').remove();
                }
            }
            else
            {
                $containers.find('.base_encrypted_field_commands').remove();
            }
            return result;
        },
        on_encrypt: function()
        {
            return instance.base_encrypted_field.get_pgp_keys(this)
            .then(function(private_key)
            {
                debugger;
            });
        },
        on_decrypt: function()
        {
            return instance.base_encrypted_field.get_pgp_keys(this)
            .then(function(private_key)
            {
                debugger;
            });
        },
    });
}
