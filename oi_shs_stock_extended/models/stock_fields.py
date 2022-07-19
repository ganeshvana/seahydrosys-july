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

    # @api.one
    # @api.depends('move_ids_without_package')
    # def _get_fcl_weight(self):
    #     for pick in self:
    #         weight = 0.00
    #         for line in pick.move_ids_without_package:
    #             weight += line.product_uom_qty * line.product_id.weight
    #             self.fcl_weight = weight

    # @api.one
    # @api.depends('origin')
    # def _get_mo(self):
    #     for pick in self:
    #         if self.origin:
    #             mo = self.env['mrp.production'].search([('name', '=', self.origin)])
    #             self.mrp_id = mo.id


    supplier_ref = fields.Char(string="Supplier's Ref")
    drawing_no = fields.Char(string='Drawing No.')
    motor_vehicle_no = fields.Char(string="Motor Vehicle No")
    duration_of_process = fields.Char(string="Duration of Process")
    nature_of_process = fields.Char(string="Nature of Process")
    destination = fields.Char(string='Destination')
    despatched_through = fields.Char('Despatched Through')
    buyer_order_no = fields.Char(string="Buyer's Order No")
    customer_reference = fields.Char(string="Customer Reference")
    # fcl_weight = fields.Float('FCL Weight',compute="_get_fcl_weight")
    # mrp_id =  fields.Many2one('mrp.production','Mo',compute="_get_mo")
  

class sale_order(models.Model):

    _inherit = 'sale.order'


    def action_confirm(self):
        res = super(sale_order, self).action_confirm()
        for rec in self:
            for pick_rec in rec.picking_ids:
                pick_rec.write({
                    'customer_reference': rec.client_order_ref
                })

        return res



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
