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
        string="Main image",
        store=False,
        compute="_compute_multi_image",
        inverse="_inverse_multi_image_main",
    )

    @api.depends("image_ids")
    def _compute_multi_image(self):
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
            "storage": "filestore",
            "owner_model": self._name,
            "owner_id": self.id,
        }
        if name:
            values["name"] = name
        image_rec = False
        if self.image_ids:
            image_rec = self.image_ids[0]
        if image:
            values.update({"attachment_image": image})
            if image_rec:
                # write
                image_rec.write(values)
            else:
                # create
                values.setdefault("name", name or _("Main image"))
                self.image_ids = [(0, 0, values)]
        else:
            # unlink
            image_rec and image_rec.unlink()

    def _inverse_multi_image_main(self):
        for owner in self:
            owner._set_multi_image(owner.image_1920)

    def unlink(self):
        """Mimic `ondelete="cascade"` for multi images.

        Will be skipped if ``env.context['bypass_image_removal']`` == True
        """
        images = self.mapped("image_ids")
        result = super().unlink()
        if result and not self.env.context.get("bypass_image_removal"):
            images.unlink()
        return result
