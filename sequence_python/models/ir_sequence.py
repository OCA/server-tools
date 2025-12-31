# Copyright 2020 Sunflower IT (<https://sunflowerweb.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import random
import string
import uuid
from inspect import getmembers, isclass, isfunction

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval, wrap_module

_logger = logging.getLogger(__name__)


# Pre-compute UUID safe members to avoid recomputation on each call
_UUID_SAFE_MEMBERS = [
    name for name, _ in getmembers(uuid, lambda m: isfunction(m) or isclass(m))
]


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
        :return: dict
        """
        wrap_random = wrap_module(random, random.__all__)
        wrap_uuid = wrap_module(uuid, _UUID_SAFE_MEMBERS)
        wrap_string = wrap_module(string, string.__all__)
        if isinstance(number_next, tuple):
            number_next = number_next[0]
        return {
            "number": number_next,
            "number_padded": f"{number_next:0{self.padding}d}",
            "sequence": self,
            "random": wrap_random,
            "uuid": wrap_uuid,
            "string": wrap_string,
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
            result = self._get_python_value(number_next)
            # Convert to string to prevent TypeError when concatenating with strings
            # Only convert if it's not already a string to preserve original behavior
            result_str = str(result) if not isinstance(result, str) else result
            return interpolated_prefix + result_str + interpolated_suffix
        else:
            return super().get_next_char(number_next)
