# Copyright 2020 Sunflower IT (<https://sunflowerweb.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import random
import string
import uuid

from odoo import fields, models
from odoo.tools import safe_eval

_logger = logging.getLogger(__name__)


DEFAULT_PYTHON_CODE = "number_padded"


class IrSequence(models.Model):
    """
    Inherit standard ir.sequence to let the possibility of using a Python formula
    to calculate the sequence from input variables such as the sequence number.
    This allows obfuscation of the order in which sequences are given out,
    but can also be used for any other purpose.
    """

    _inherit = "ir.sequence"

    # Python code
    use_python_code = fields.Boolean(string="Use Python", default=False)
    python_code = fields.Text(
        string="Python expression",
        default=DEFAULT_PYTHON_CODE,
        help="Write Python code that generates the sequence body.",
    )
    python_code_preview = fields.Char("Preview", compute="_compute_python_code_preview")

    def _get_python_eval_context(self, number_next):
        """
        Get the eval context to evaluate the Python code with.
        The format is (variable name, description, value)
        You can inherit this in your custom module.
        :return: tuple
        """
        return {
            "number": number_next[0] if isinstance(number_next, tuple) else number_next,
            "number_padded": "%%0%sd" % self.padding % number_next,
            "sequence": self,
            "random": random,
            "uuid": uuid,
            "string": string,
        }

    def _get_python_value(self, number_next):
        """
        Use the python formula to get the value.
        :return: string
        """
        eval_context = self._get_python_eval_context(number_next)
        return safe_eval(self.python_code.strip(), eval_context)

    def _compute_python_code_preview(self):
        for this in self:
            try:
                this.python_code_preview = self.get_next_char(
                    (self.number_next_actual,)
                )
            except Exception as e:  # noqa
                this.python_code_preview = str(e)

    def get_next_char(self, number_next):
        if self.use_python_code:
            interpolated_prefix, interpolated_suffix = self._get_prefix_suffix()
            return (
                interpolated_prefix
                + self._get_python_value(number_next)
                + interpolated_suffix
            )
        else:
            return super().get_next_char(number_next)
