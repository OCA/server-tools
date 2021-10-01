odoo.define("base_changeset.form_backend", function(require) {
    "use strict";

    var FormRenderer = require("web.FormRenderer");
    var FormController = require("web.FormController");
    var core = require("web.core");
    var qweb = core.qweb;

    FormController.include({
        start: function() {
            return this._super
                .apply(this, arguments)
                .then(this._updateChangeset.bind(this));
        },

        update: function() {
            var self = this;
            var res = this._super.apply(this, arguments);
            res.then(function() {
                self._updateChangeset();
            });
            return res;
        },

        _updateChangeset: function() {
            var self = this;
            var state = this.model.get(this.handle);
            this.model
                .getChangeset(state.model, state.data.id)
                .then(function(changeset) {
                    self.renderer.renderChangesetPopovers(changeset);
                });
        },

        applyChange: function(id) {
            this.model.applyChange(id).then(this.reload.bind(this));
        },

        rejectChange: function(id) {
            this.model.rejectChange(id).then(this.reload.bind(this));
        },
    });

    FormRenderer.include({
        renderChangesetPopovers: function(changeset) {
            var self = this;
            _.each(changeset, function(changes, fieldName) {
                var labelId = self._getIDForLabel(fieldName);
                var $label = self.$el.find(_.str.sprintf('label[for="%s"]', labelId));
                if (!$label.length) {
                    var widgets = _.filter(
                        self.allFieldWidgets[self.state.id],
                        function(widget) {
                            return widget.name === fieldName;
                        }
                    );
                    if (widgets.length === 1) {
                        var widget = widgets[0];
                        $label = widget.$el;
                    } else {
                        return;
                    }
                }
                self._renderChangesetPopover($label, changes);
            });
        },

        _renderChangesetPopover: function($el, changes) {
            var self = this;
            if (this.mode !== "readonly") {
                return;
            }
            var $button = $(
                qweb.render("ChangesetButton", {
                    count: changes.length,
                })
            );

            $el.append($button);

            var options = {
                content: function() {
                    var $content = $(
                        qweb.render("ChangesetPopover", {
                            changes: changes,
                        })
                    );
                    $content.find(".base_changeset_apply").on("click", function() {
                        self._applyClicked($(this));
                    });
                    $content.find(".base_changeset_reject").on("click", function() {
                        self._rejectClicked($(this));
                    });
                    return $content;
                },
                html: true,
                placement: "bottom",
                title: "Pending Changes",
                trigger: "focus",
                delay: {show: 0, hide: 100},
                template: qweb.render("ChangesetTemplate"),
            };

            $button.popover(options);
        },

        _applyClicked: function($el) {
            var id = parseInt($el.data("id"), 10);
            this.getParent().applyChange(id);
        },

        _rejectClicked: function($el) {
            var id = parseInt($el.data("id"), 10);
            this.getParent().rejectChange(id);
        },
    });
});
