from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time



class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    current_address = fields.Many2one(
        'res.partner', string='Current Address')
