# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from openerp.tests.common import TransactionCase

IMAGE = """
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A/wD
/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9gLBxAeE5Rn4DsAAAJtSURBVDjLjZJdSF
NxGMaf/znH09bOJrKzLedHN+fsbNQcU9qNo2SWpEISeWFX1V1XJnhVBEOIoLskCMqrIkIJxIsoQggzN
LwwDTRMvJBgfjTxg7m5ne2ct4tsVGzkc/Xy/h9+PP+HFygjVdWeK4qa8/v9u+Fwc385H19qqWnaRdM0
HgAQOI6ziCJrk6Sq1e3t5Jd/vVwZbpMsu5hosUJ2uZHPF0Ck95RylgSIom2r3luF0ZGniN/thyw7AcB
2ZICuZ9duX09AsdxEtD6OWCgFcLZKVdUsRwJwPJN3Ci1IJDxI5TpQsF+A3VbRAKAT/5OiKFpv763V1H
6G1hLrVDCJJic/UDAYJEVRvvp8Wk3ZBKqqcQAet7bGTko2K9weN2AaCIVCcLncABAgwhOfT2MlAURGp
LGx6Vws1gKAwBiBMcDhcGBgIA5ZlsFx6CBCS7kOrnV1XeIlyQFdz4GIig/RaBTV1dUwDJMRIfZ7LxSP
Rw3U2qRjV73eOgCAaRJ4ngAwAASAgyTZD2dU/QWYGmpw7uyhrbYmKy18G8V6IAiPyw4isxjUnO8Gn10
GwKM9KoqPVv7IvfSqcSz7KUg010AzzxS6crmTFhaX6JdM0g2izPsIfX+h0cygn9KvA1upsdPdxQ4qWE
EQBIZchnDGJ6I9vIH99MEhnuHtm3FMzxmoO8EQOcVgtcCp53Gv+IV0yqzd/sFgtQDicR5d4QIGhx9iZ
NhDmxsJzM7Osxtn82gNCzhIA4tLmEgmhftFwOKyef7jZ4pkDTR7K1n7+m7e+W5qumcnQ3OHVVWsbAp9
4xPmnUSSDX3fQ1/85bwJAD8BBuHrn9G4ZlgAAAAASUVORK5CYII="""


class TestMailMessage(TransactionCase):

    def setUp(self):
        super(TestMailMessage, self).setUp()
        self.mail_message = self.env['mail.message']
        self.ir_attachment = self.env['ir.attachment']

    def test_create(self):
        file_name = 'file_name'
        cid = '<42>'
        full_name = '%s%s' % (file_name, cid)
        attach_vals = {
            'name': full_name,
            'datas': base64.b64encode(str(IMAGE)),
            'datas_fname': full_name,
            'description': full_name,
            'res_model': 'res.partner',
            'res_id': self.env.ref('base.partner_root').id,
        }
        vals = {
            'subject': 'test',
            'body': '<body><img src="cid:42"></body>',
            'attachment_ids': [(0, 0, attach_vals)]
        }
        mail_message_id = self.mail_message.create(vals)
        self.assertTrue(
            mail_message_id.attachment_ids, 'Should have attachment')
        self.assertEqual(
            mail_message_id.attachment_ids.name,
            file_name, 'Should have only the file_name')
        self.assertTrue(
            mail_message_id.attachment_ids._get_image_url().replace(
                '&', '&amp;') in mail_message_id.body,
            'Should have a correct Odoo url')
