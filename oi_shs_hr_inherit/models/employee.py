from odoo import api, fields, models, tools, _



class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    current_address = fields.Many2one(
        'res.partner', string='Current Address')




class ContractHistory(models.Model):
    _inherit = "hr.contract"
    _description = "Contract"

    years_of_experience = fields.Char(
       string='Years of Experience', compute='_compute_years_of_experience')
    
    
    @api.depends('date_start','date_end')
    def _compute_years_of_experience(self):
        for record in self:
            start_date = fields.Date.from_string(record.date_start)
            end_date =  fields.Date.from_string(record.date_end)
            today_date = fields.Date.from_string(fields.Date.today())
            if record.date_start and not record.date_end:
                delta = today_date - start_date
                years_of_experience = delta.days // 365  # Approximate number of years
                record.years_of_experience = str(years_of_experience)
            elif record.date_start and record.date_end:
                delta = end_date - start_date
                years_of_experience = delta.days // 365  # Approximate number of years
                record.years_of_experience = str(years_of_experience)
            else:
                record.years_of_experience = 'N/A'
            
    