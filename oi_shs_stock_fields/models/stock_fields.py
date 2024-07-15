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
            weight += line.total 
        pick.fcl_weight = weight
                
    @api.depends('move_ids_without_package')
    def _get_done_total(self):  
        for pick in self:
            done = 0.00
        for line in pick.move_ids_without_package:
            done +=line.quantity_done
        pick.done_total = done

    # @api.depends('origin')
    # def _get_mo(self):
    #     for pick in self:
    #         if self.origin:
    #             mo = self.env['mrp.production'].search([('name', '=', self.origin)])
    #             self.mrp_id = mo.id
    
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
    fcl_weight = fields.Float('Net Weight', compute="_get_fcl_weight")
    gross_weight = fields.Float('Gross Weight')
    done_total = fields.Float('Total Quantity',compute="_get_done_total")
    mrp_id =  fields.Many2one('mrp.production','Mo',compute="_get_mo")
    drawing_no = fields.Char("Drawing No")
    categ_id = fields.Many2one('product.category','Product Category',related='product_id.categ_id',store=True,)


class stock_move(models.Model):
    _inherit = 'stock.move'
    
    description = fields.Char('Customer Reference',readonly=False)
    weight = fields.Float(related='product_id.weight',string="weight in (kg)",compute='_compute_weight')
    gross = fields.Float(string="Gross Weight")
    total = fields.Float(string="Total Weight",compute='_compute_total')
    
    @api.depends('product_id')
    def _compute_weight(self):
        for record in self:
            record.weight =  record.product_id.weight
        

    @api.depends('quantity_done', 'weight')
    def _compute_total(self):
        for record in self:
            record.total = record.quantity_done * record.product_id.weight  
            
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    weight = fields.Float(related='product_id.weight',string="Weight in (kg)" ,store=True)

  




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
