
openerp.binary_field = function (instance) {
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.form.widgets.add('imagefield', 
            'instance.web.form.ImageField');
    console.log(instance.web.form.widgets);

    instance.web.form.is_url = function(v) {
        var regexp = new RegExp("^((http|https):\/\/)?(www[.])?([a-zA-Z0-9]|-)+([.][a-zA-Z0-9(-|\/|=|?)?]+)+$");
        return regexp.test(v);
    };

    instance.web.form.FieldBinaryImage.include({
        render_value: function() {
            var self = this;
            var url;
            if (this.get('value') && instance.web.form.is_url(this.get('value'))) {
                console.log('we got it!!!');
                url = this.get('value');
                var $img = $(QWeb.render("FieldBinaryImage-img",
                             { widget: this, url: url }));
                this.$el.find('> img').remove();
                this.$el.prepend($img);
                $img.load(function() {
                    if (! self.options.size)
                        return;
                    $img.css("max-width", "" + self.options.size[0] + "px");
                    $img.css("max-height", "" + self.options.size[1] + "px");
                    $img.css("margin-left", ""
                             + (self.options.size[0] - $img.width()) / 2
                             + "px");
                    $img.css("margin-top", ""
                             + (self.options.size[1] - $img.height()) / 2
                             + "px");
                });
                $img.on('error', function() {
                    $img.attr('src', self.placeholder);
                    instance.webclient.notification.warn(
                        _t("Image"),
                        _t("Could not display the selected image."));
                });
            } else {
                return this._super()
            };
        }});


    instance.web_kanban.KanbanRecord.include({
        kanban_image: function(model, field, id, cache, options) {
            console.log(this.record[field].value)
            if (this.record[field]
                && this.record[field].value
                && instance.web.form.is_url(this.record[field].value)
            ) {
                return this.record[field].value;
            } else {
                return this._super();
            }
        },
    })

};
