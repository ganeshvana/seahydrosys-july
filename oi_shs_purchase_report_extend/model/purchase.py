from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import timedelta

class picking(models.Model):
    _inherit = "stock.picking"
    
    todo_date = fields.Date("To Do Date")
    
    def button_validate(self):
        result = super(picking, self).button_validate()
        internal = self.env['stock.picking'].search([('origin', '=', self.origin), ('picking_type_code', '=', 'internal')])
        if internal:        
            internal.todo_date = fields.Date.today()  +  timedelta(days=3)
        return result

class purchase_order(models.Model):
    _inherit = "purchase.order"
 
    # mo_product = fields.Char("MO Product",compute="_get_mo_product")   
    despatch_through = fields.Char(string="Despatch Through")
    due_date = fields.Date("Due Date")
    sail_date = fields.Date("Sail Date")
    tax_country_id = fields.Many2one("res.country",'Country')
    # pick_id = fields.Many2one('stock.picking','DO')
    

    # @api.depends('origin')
    # def _get_mo_product(self):
    #     self.mo_product = ''
    #     for order in self:
    #         if self.origin:
    #             mo = self.env['mrp.production'].search([('name', '=', self.origin)])
    #             if mo:
    #             	self.mo_product = mo.product_id.name
    #             else:
    #                 self.mo_product = ''

    # def action_mo(self):
    #     for order in self:
    #         for line in order.order_line:
    #             if order.mo_product:
    #                 line.write({'name':order.mo_product})









class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"
 
   
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Purchase Price'))


class accoount_invoice_line(models.Model):
    _inherit = "account.move.line"
 
   
    price_unit = fields.Float(string='Price', digits=dp.get_precision('Purchase Price'))


   
