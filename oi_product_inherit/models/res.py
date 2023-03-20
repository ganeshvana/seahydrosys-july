from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time



class ResCompany(models.Model):
    _inherit = "res.company"

    dated = fields.Date("Dated")
    from_date = fields.Date("From")
    to_date = fields.Date("To")
    company_qr = fields.Binary(string="Company QR")
    lut_line_ids = fields.One2many('lut.timeline','lut_line_id', string="LUT Timeline")
    # computed_field = fields.Integer(compute='_compute_field', string="Computed Field")



    # def _compute_field(self):
    #     for record in self:
    #         if record.from_date and record.to_date:
    #             start_date = datetime.strptime(record.from_date, '%Y-%m-%d').date()
    #             end_date = datetime.strptime(record.to_date, '%Y-%m-%d').date()
    #             domain = [('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date)]
    #             records_in_period = self.search(domain)
    #             for rec in records_in_period:
    #                 print(rec.lut_line_id.lut_bond_no)
class ResCompany(models.Model):
    _inherit = "account.move"

    from_date = fields.Date("From")
    to_date = fields.Date("To") 
    dated = fields.Date("Dated")
    lut_bond_no = fields.Char("LUT/Bond No")

                                 
    @api.model
    def create(self,vals):      
        res = super(ResCompany, self).create(vals) 
        if res.company_id and res.invoice_date:
            lut_entry =  res.company_id.lut_line_ids.filtered(lambda m: m.from_date <= res.invoice_date and m.to_date >= res.invoice_date)
            if lut_entry:
                res.lut_bond_no = lut_entry.lut_bond_no
                res.from_date = lut_entry.from_date
                res.to_date = lut_entry.to_date
                res.dated = lut_entry.dated

        return res
        
    @api.model
    def write(self,vals):      
        result = super(ResCompany, self).write(vals) 
        print(vals, "vvals----------")
        if 'invoice_date' in vals:
            for res in self:
                if res.company_id and res.invoice_date:
                    lut_entry =  res.company_id.lut_line_ids.filtered(lambda m: m.from_date <= res.invoice_date and m.to_date >= res.invoice_date)
                    if lut_entry:
                        res.lut_bond_no = lut_entry.lut_bond_no
                        res.from_date = lut_entry.from_date
                        res.to_date = lut_entry.to_date
                        res.dated = lut_entry.dated


        return result





            


class LutTimeline(models.Model):
    _name = "lut.timeline"

    lut_line_id = fields.Many2one('res.company',"LUT Timeline")
    from_date = fields.Date("From Date")  
    to_date = fields.Date("To Date")
    dated = fields.Date("Dated")
    lut_bond_no = fields.Char("LUT/Bond No")
    computed_field = fields.Integer(compute='_compute_field', string="Computed Field")
   