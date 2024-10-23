# Copyright 2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Module overrides part of base_import to restore support for xlsx files."""
import datetime
import io

from odoo import _, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

# pylint: disable=import-error
from odoo.addons.base_import.models.base_import import FILE_TYPE_DICT

try:
    import openpyxl
except ImportError:
    openpyxl = None


FILE_TYPE_DICT["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"] = (
    "xlsx",
    openpyxl,
    "openpyxl",
)


class BaseImport(models.TransientModel):
    """Contains the method to read xlsx files."""

    _inherit = "base_import.import"

    def _read_xlsx(self, options):
        """Read modern excel file using openpyxl.

        Override method from super, that points back to _read_xls.
        """
        # pylint: disable=unused-argument
        buffer = io.BytesIO(self.file or b"")
        # read_only=False is needed because of a bug in openpyxl, combined with
        # some providers of excel files not setting the correct dimensions.
        book = openpyxl.load_workbook(
            buffer, read_only=False, keep_vba=False, data_only=True, keep_links=False
        )
        sheet = book.worksheets[0]
        for row in sheet.rows:
            values = []
            for cell in row:
                if isinstance(cell, openpyxl.cell.read_only.EmptyCell):
                    values.append("")
                    continue
                # Would like to skipp NULL values, but for some incomprehensible
                # reason TYPE_NULL and TYPE_NUMERIC have the same value in openpyxl.
                if cell.value is None:
                    values.append("")
                    continue
                if cell.data_type == "d" and isinstance(cell.value, datetime.date):
                    is_date = not isinstance(
                        cell.value, datetime.datetime
                    ) or cell.value.time() == datetime.time(0, 0, 0)
                    # Date, time or datetime.
                    if is_date:
                        values.append(cell.value.strftime(DEFAULT_SERVER_DATE_FORMAT))
                    else:
                        values.append(
                            cell.value.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        )
                    continue
                if cell.data_type is openpyxl.cell.cell.TYPE_NUMERIC:
                    is_float = cell.value % 1 != 0.0
                    values.append(str(cell.value) if is_float else str(int(cell.value)))
                    continue
                if cell.data_type is openpyxl.cell.cell.TYPE_BOOL:
                    values.append("True" if cell.value else "False")
                    continue
                if cell.data_type is openpyxl.cell.cell.TYPE_ERROR:
                    raise ValueError(
                        _("Invalid cell value in cell %(coordinate)s: %(cell_value)s")
                        % {
                            "coordinate": cell.coordinate,
                            "cell_value": cell.check_error(),
                        }
                    )
                values.append(str(cell.value))
            if any(x for x in values if x.strip()):
                yield values
        book.close()
