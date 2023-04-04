# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class Owner(models.AbstractModel):
    _name = "base_multi_image.owner"
    _description = """ Wizard for base multi image """

    image_ids = fields.One2many(
        comodel_name="base_multi_image.image",
        inverse_name="owner_id",
        string="Images",
        domain=lambda self: [("owner_model", "=", self._name)],
        copy=True,
    )
    image_1920 = fields.Image(
        store=False,
        compute="_compute_image_1920",
        inverse="_inverse_image_1920",
    )

    @api.depends("image_ids")
    def _compute_image_1920(self):
        """Get the main image for this object.

        This is provided as a compatibility layer for submodels that already
        had one image per record.
        """
        for s in self:
            first = s.image_ids[:1]
            s.image_1920 = first.image_1920

    def _set_multi_image(self, image=False, name=False):
        """Save or delete the main image for this record.

        This is provided as a compatibility layer for submodels that already
        had one image per record.
        """
        # Values to save
        values = {
            "storage": "db",
            "file_db_store": image,
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

    def _inverse_image_1920(self):
        self._set_multi_image(self.image_1920)

    def unlink(self):
        """Mimic `ondelete="cascade"` for multi images.

        Will be skipped if ``env.context['bypass_image_removal']`` == True
        """
        images = self.mapped("image_ids")
        result = super().unlink()
        if result and not self.env.context.get("bypass_image_removal"):
            images.unlink()
        return result
