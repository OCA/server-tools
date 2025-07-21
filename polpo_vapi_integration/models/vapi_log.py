from odoo import api, models, fields
from datetime import timedelta

class VapiLog(models.Model):
    _name = "vapi.log"
    _description = "Vapi call log"
    _rec_name = 'call_id'
    _order = "start_time desc"


    user_id = fields.Many2one('res.users', string="User", required=True, help="The user who made the call")
    call_id = fields.Char("Odoo Call ID", required=True, help="Unique identifier for the call")
    start_time = fields.Datetime("Start", required=True, help="Date and time when the call started")
    end_time = fields.Datetime("End", help="Date and time when the call ended")
    duration = fields.Integer("Duration (sec.)", help="Call duration in seconds, 0 if not ended")
    state = fields.Selection([
        ('started', "Started"),
        ('in_progress', "In Progress"),
        ('finished', "Ended"),
        ('error', "Error"),
    ], string="Call Status", default="in_progress", required=True,
        help="The current status of the call. 'Started' when initiated, 'In Progress' during the call, 'Ended' when completed, and 'Error' if there was an issue.")
    last_active = fields.Datetime("Last activity", help="Date and time of the last activity in the call, used to determine if the call is stuck")
    duration_str = fields.Char('Duration', compute='_compute_duration_str', store=False)

    def _compute_duration_str(self):
        for record in self:
            if record.duration is not None:
                hours = record.duration // 3600
                minutes = (record.duration % 3600) // 60
                seconds = record.duration % 60
                record.duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                record.duration_str = "00:00:00"

    @api.model
    def cron_close_stuck_calls(self, minutes=10):
        """
        Closes calls that have been stuck for more than a specified number of minutes.
        """
        dt_limit = fields.Datetime.to_string(
            fields.Datetime.from_string(fields.Datetime.now()) - timedelta(minutes=minutes)
        )
        stuck_calls = self.search([
            ('state', 'in', ['started', 'in_progress']),
            '|',
            ('last_active', '=', False),
            ('last_active', '<', dt_limit)
        ])
        for rec in stuck_calls:
            rec.write({
                'state': 'error',
                'end_time': fields.Datetime.now(),
                'duration': rec.start_time and int((fields.Datetime.now() - rec.start_time).total_seconds()) or 0,
            })