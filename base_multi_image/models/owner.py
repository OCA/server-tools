# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


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

    def unlink(self):
        """Mimic `ondelete="cascade"` for multi images.

        Will be skipped if ``env.context['bypass_image_removal']`` == True
        """
        images = self.mapped("image_ids")
        result = super().unlink()
        if result and not self.env.context.get("bypass_image_removal"):
            images.unlink()
        return result
