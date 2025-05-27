# Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_DEFAULT_CODE = _(
    "# ---Predefined Variables--- #\n"
    "# All variables allowed in a server action such as:\n"
    "#  - env: Odoo environment in which the action is triggered.\n"
    "#  - model: Odoo model of the record on which the action is triggered.\n"
    "#  - record: record on which the action is triggered.\n"
    "#  - records: set of records on which the action is triggered.\n"
    "#  - time, datetime, dateutil, timezone: useful Python libraries.\n"
    "#  - log(message, level='info'): logging function to log debugging information "
    "in the ir.logging table.\n"
    "#  - UserError: Exception warning for use with raise.\n"
    "#  - To return an action, assign: action = {...}\n"
    "# Variable names: configured in the 'Unique Name' field.\n"
    "#  - These will contain the value entered in the input box.\n"
    "#  - Indicates the data type: 'string', 'int', 'float' 'boolean'.\n"
    "#  - Input lists, tuples, sets, and dictionaries as 'string' and perform "
    "the conversion in your code.\n\n\n"
)


class ServerActionInputBox(models.Model):
    _name = "server.action.input.box"
    _description = "Server Action Input Box"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    server_action_input_box_line_ids = fields.One2many(
        comodel_name="server.action.input.box.line",
        inverse_name="server_action_input_box_id",
        string="Parameter lines",
    )
    code = fields.Text(string="Python code", default=_DEFAULT_CODE)
    cancel_button = fields.Boolean("Add cancel button", default=True)
    ir_action_server_id = fields.Many2one("ir.actions.server", string="Server action")
    model_id = fields.Many2one(
        "ir.model", string="Model", required=True, ondelete="cascade"
    )
    show_confirmation_dialog = fields.Boolean(
        string="Ask for confirmation", default=True
    )
    apply_to_linked_field_lines = fields.Boolean(default=False)
    linked_field_lines_id = fields.Many2one(
        "ir.model.fields",
        string="Linked field",
        domain="[('model_id', '=', model_id), ('ttype', '=', 'one2many')]",
    )

    def _code_ir_action_server(self):
        lines_code = self.code.splitlines()
        indent = "  "
        indent_lines = "\n".join([indent + line for line in lines_code])

        parameters = ""
        for line in self.server_action_input_box_line_ids:
            parameters += indent + line.name + f" = parsed_parameters['{line.name}']\n"

        code = '''# """ Fixed code block """ #
context = env.context
do_action = context.get('do_action', False)
server_action_input_box_id = env['server.action.input.box'].browse({})

if do_action:
  model_name = context.get('model_name', False)
  records_ids =context.get('records_ids', False)
  parameters = context.get('parameters', False)
  original_context = context.get('context', False)
  model = env[model_name]
  records = model.browse(records_ids)
  record = records[0]
  parsed_parameters = server_action_input_box_id.parsed_parameters(parameters)

{}
# """ End of fixed code block """ #
  # Here begins the custom code

{}

  # Here ends the custom code
# """ Fixed code block """ #
else:
  action = server_action_input_box_id.show_input_box(records,context)
# """ End of fixed code block """ #'''.format(
            self.id, parameters, indent_lines
        )
        return code

    def _write_ir_action_server(self):
        code = self._code_ir_action_server()
        if self.active:
            model_id = self.model_id.id
        else:
            model_id = None
        ir_action_server_id = self.ir_action_server_id
        if not ir_action_server_id:
            ir_action_server_id = self._create_ir_action_server()
        self.ir_action_server_id = None
        ir_action_server_id.write(
            {
                "name": self.name,
                "model_id": self.model_id.id,
                "state": "code",
                "code": code,
                "binding_model_id": model_id,
                "binding_type": "action",
            }
        )
        self.ir_action_server_id = ir_action_server_id

    # We create the server action that will call the input box
    def _create_ir_action_server(self):
        code = self._code_ir_action_server()

        if self.active:
            model_id = self.model_id.id
        else:
            model_id = None

        ir_action_server_id = self.env["ir.actions.server"].create(
            {
                "name": self.name,
                "model_id": self.model_id.id,
                "state": "code",
                "code": code,
                "binding_model_id": model_id,
                "binding_type": "action",
            }
        )

        return ir_action_server_id

    def show_input_box(self, records, context):
        if self.apply_to_linked_field_lines and self.linked_field_lines_id:
            records = getattr(records[0], self.linked_field_lines_id.name)

        return {
            "name": self.name,
            "type": "ir.actions.client",
            "tag": "show_server_action_input_box",
            "target": "new",
            "params": {
                "line_ids": self.server_action_input_box_line_ids.ids,
                "id": self.id,
                "show_confirmation_dialog": self.show_confirmation_dialog,
                "records_ids": records.ids,
                "binding_model": records._name,
                "context": context,
            },
        }

    def do_action(self, model_name, records_ids, parameters_dict, context):
        custom_context = {
            "records_ids": records_ids,
            "parameters": parameters_dict,
            "model_name": model_name,
            "do_action": True,
        }
        # Para evitar modificar el diccionario original (mala práctica)
        new_context = dict(context or {})  # `or {}` por si llega None
        new_context.update(custom_context)

        action_server = self.ir_action_server_id
        run_server = action_server.with_context(**new_context).sudo().run()
        return run_server

    def _get_data_type_conversion(self):
        return {
            "string": lambda s: s,
            "int": int,
            "float": float,
            "bool": lambda b: b,
        }
    
    def _get_raw_data(self, line, parameters):
        raw_value = parameters.get(line.name)
        return raw_value or 0 if line.data_type != "string" else raw_value

    def parsed_parameters(self, parameters):
        parsed_parameters_dict = {}
        data_type_conversion = self._get_data_type_conversion()

        for line in self.server_action_input_box_line_ids:
            raw_data = self._get_raw_data(line, parameters)
            try:
                convert_data = data_type_conversion[line.data_type]
                data = convert_data(raw_data)
            except ValueError as e:
                raise UserError(
                    _(
                        "The value '%(param_value)s' for '%(param_name)s' "
                        "is not of type '%(data_type)s'."
                    )
                    % {
                        "param_value": parameters.get(line.name),
                        "param_name": line.name,
                        "data_type": line.data_type,
                    }
                ) from e

            parsed_parameters_dict[line.name] = data

        return parsed_parameters_dict

    def write(self, vals):
        record = super(ServerActionInputBox, self).write(vals)
        if "ir_action_server_id" not in vals:
            self._write_ir_action_server()
        return record

    @api.model_create_multi
    def create(self, vals):
        record = super(ServerActionInputBox, self).create(vals)
        record.ir_action_server_id = record._create_ir_action_server()
        return record

    def unlink(self):
        ir_action_server_id = self.ir_action_server_id
        record = super(ServerActionInputBox, self).unlink()
        if ir_action_server_id:
            ir_action_server_id.unlink()
        return record
