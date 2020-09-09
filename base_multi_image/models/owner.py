# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models, tools


class Owner(models.AbstractModel):
    _name = "base_multi_image.owner"
    _description = """ Wizard for base multi image """

    image_ids = fields.One2many(
        comodel_name='base_multi_image.image',
        inverse_name='owner_id',
        string='Images',
        domain=lambda self: [("owner_model", "=", self._name)],
        copy=True)
    image_main = fields.Binary(
        string="Main image",
        store=False,
        compute="_get_multi_image",
        inverse="_set_multi_image_main")
    image_main_medium = fields.Binary(
        string="Medium image",
        compute="_get_multi_image",
        inverse="_set_multi_image_main_medium",
        store=False)
    image_main_small = fields.Binary(
        string="Small image",
        compute="_get_multi_image",
        inverse="_set_multi_image_main_small",
        store=False)

    @api.depends('image_ids')
    def _get_multi_image(self):
        """Get the main image for this object.

        This is provided as a compatibility layer for submodels that already
        had one image per record.
        """
        for s in self:
            first = s.image_ids[:1]
            s.image_main = first.image_main
            s.image_main_medium = first.image_medium
            s.image_main_small = first.image_small

    def _set_multi_image(self, image=False, name=False):
        """Save or delete the main image for this record.

        This is provided as a compatibility layer for submodels that already
        had one image per record.
        """
        # Values to save
        values = {
            "storage": "db",
            "file_db_store": tools.image_resize_image_big(image),
            "owner_model": self._name,
        }
        if name:
            values["name"] = name

        for s in self:
            if image:
                values["owner_id"] = s.id
                # Editing
                if s.image_ids:
                    s.image_ids[0].write(values)
                # Adding
                else:
                    values.setdefault("name", name or _("Main image"))
                    s.image_ids = [(0, 0, values)]
            # Deleting
            elif s.image_ids:
                s.image_ids[0].unlink()

    def _set_multi_image_main(self):
        self._set_multi_image(self.image_main)

    def _set_multi_image_main_medium(self):
        self._set_multi_image(self.image_main_medium)

    def _set_multi_image_main_small(self):
        self._set_multi_image(self.image_main_small)

    def unlink(self):
        """Mimic `ondelete="cascade"` for multi images.

        Will be skipped if ``env.context['bypass_image_removal']`` == True
        """
        images = self.mapped("image_ids")
        result = super(Owner, self).unlink()
        if result and not self.env.context.get('bypass_image_removal'):
            images.unlink()
        return result
