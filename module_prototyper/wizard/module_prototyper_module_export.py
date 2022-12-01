# #############################################################################
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2010 - 2014 Savoir-faire Linux
# (<http://www.savoirfairelinux.com>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import os
import zipfile
from collections import namedtuple
from io import BytesIO

from odoo import fields, models


class PrototypeModuleExport(models.TransientModel):
    _name = "module_prototyper.module.export"
    _description = "Module Prototype module export"

    def _default_api_version(self):
        return self.env.ref("module_prototyper.api_version_140").id

    name = fields.Char("File Name", readonly=True)
    api_version = fields.Many2one(
        comodel_name="module_prototyper.api_version",
        string="API version",
        required=True,
        default=_default_api_version,
    )
    data = fields.Binary("File", readonly=True)
    state = fields.Selection(
        [("choose", "choose"), ("get", "get")],  # choose version  # get module
        default="choose",
    )

    def action_export(self):
        """
        Export a zip file containing the module based on the information
        provided in the prototype, using the templates chosen in the wizard.
        """
        active_model = self._context.get("active_model")

        # checking if the wizard was called by a prototype.
        msg = '%s has to be called from a "module_prototyper" , not a "%s"'
        assert active_model == "module_prototyper", msg % (self, active_model)

        # getting the prototype of the wizard
        prototypes = self.env[active_model].browse([self._context.get("active_id")])

        zip_details = self.zip_files(self, prototypes)

        if len(prototypes) == 1:
            zip_name = prototypes[0].name
        else:
            zip_name = "prototyper_export"

        self.write(
            {
                "name": "{}.zip".format(zip_name),
                "state": "get",
                "data": base64.encodebytes(zip_details.BytesIO.getvalue()),
            }
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": "module_prototyper.module.export",
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    @staticmethod
    def zip_files(wizard, prototypes):
        """Takes a set of file and zips them.
        :param file_details: tuple (filename, file_content)
        :return: tuple (zip_file, stringIO)
        """
        zip_details = namedtuple("Zip_details", ["zip_file", "BytesIO"])
        out = BytesIO()

        with zipfile.ZipFile(out, "w") as target:
            for prototype in prototypes:
                # setting the jinja environment.
                # They will help the program to find the template to render the
                # files with.
                prototype.setup_env(wizard.api_version)

                # generate_files ask the prototype to investigate the input and
                # to generate the file templates according to it.  zip_files,
                # in another hand, put all the template files into a package
                # ready to be saved by the user.
                file_details = prototype.generate_files()
                for filename, file_content in file_details:
                    if isinstance(file_content, str):
                        file_content = file_content.encode("utf-8")
                    # Prefix all names with module technical name
                    filename = os.path.join(prototype.name, filename)
                    info = zipfile.ZipInfo(filename)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 2175008768  # specifies mode 0644
                    target.writestr(info, file_content)

            return zip_details(zip_file=target, BytesIO=out)
