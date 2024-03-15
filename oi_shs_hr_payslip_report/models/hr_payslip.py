from odoo import models, fields, api, _

class StylAccount(models.Model):
    _inherit = "hr.payslip"
    
    def print_payslip_report(self)    :
        return self.env.ref('oi_shs_hr_payslip_report.action_print_report_hr_payslip').report_action(self)


class StylAccount(models.Model):
    _inherit = "hr.employee"
    
    father_name = fields.Char("Father's Name")
    
    