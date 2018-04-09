# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
from odoo import fields


class BinaryValidated(fields.Binary):

    _slots = {
        'allowed_mimetypes': (),
    }

    def write(self, records, value, create=False):
        if not self.allowed_mimetypes:
            return super().write(records, value, create=create)
        # NOTE: no hook... we are force to override everything :(
        assert self.attachment
        if create:
            atts = records.env['ir.attachment'].sudo()
        else:
            atts = records.env['ir.attachment'].sudo().search([
                ('res_model', '=', records._name),
                ('res_field', '=', self.name),
                ('res_id', 'in', records.ids),
            ])
        with records.env.norecompute():
            if value:
                atts = atts.with_context(
                    # NOTE: actually the only change is this
                    allowed_mimetypes=self.allowed_mimetypes,
                )
                # update the existing attachments
                atts.write({'datas': value})
                # create the missing attachments
                for record in (
                        records - records.browse(atts.mapped('res_id'))):
                    atts.create({
                        'name': self.name,
                        'res_model': record._name,
                        'res_field': self.name,
                        'res_id': record.id,
                        'type': 'binary',
                        'datas': value,
                    })
            else:
                atts.unlink()
