from odoo import api, fields, models, tools, _



class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    current_address = fields.Many2one(
        'res.partner', string='Current Address')




# class ContractHistory(models.Model):
#     _inherit = "hr.contract"
#     _description = "Contract"

#     years_of_experience = fields.Char(
#        string='Years of Experience')