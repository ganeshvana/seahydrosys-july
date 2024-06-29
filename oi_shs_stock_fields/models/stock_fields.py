# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
#
from odoo import models, fields, api, _
from datetime import datetime
    
class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    @api.depends('move_ids_without_package')
    def _get_fcl_weight(self):
        for pick in self:
            weight = 0.00
        for line in pick.move_ids_without_package:
            weight += line.weight * line.quantity_done
        pick.fcl_weight = weight
        
    @api.depends('move_ids_without_package')
    def _get_done_total(self):  
        for pick in self:
            done = 0.00
        for line in pick.move_ids_without_package:
            done +=line.quantity_done
        pick.done_total = done
                
    @api.depends('origin')
    def _get_mo(self):
        for pick in self:
            if pick.origin:  
                mo = self.env['mrp.production'].search([('name', '=', pick.origin)])
                if mo:
                    pick.mrp_id = mo[0].id  
                else:
                    pick.mrp_id = False  



    supplier_ref = fields.Char(string="Supplier's Ref")
    motor_vehicle_no = fields.Char(string="Motor Vehicle No")
    duration_of_process = fields.Char(string="Duration of Process")
    nature_of_process = fields.Char(string="Nature of Process")
    destination = fields.Char(string='Destination')
    despatched_through = fields.Char('Despatched Through')
    buyer_order_no = fields.Char(string="Buyer's Order No")
    fcl_weight = fields.Float('Total Weight',compute="_get_fcl_weight")
    mrp_id =  fields.Many2one('mrp.production','Mo',compute="_get_mo")
    drawing_no = fields.Char("Drawing No")
    categ_id = fields.Many2one('product.category','Product Category',related='product_id.categ_id',store=True,)
    done_total = fields.Float('Total Quantity',compute="_get_done_total")



class stock_move(models.Model):
    _inherit = 'stock.move'
    
    description = fields.Char('Customer Reference')
    weight = fields.Float(related='product_id.weight',string="Weight in (kg)",store=True)


# class CurrencyRate(models.Model):
#     _inherit = 'res.currency.rate'

#     rate = fields.Float(digits=(12, 15), default=1.0, help='The rate of the currency to the currency of rate 1')

  




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
