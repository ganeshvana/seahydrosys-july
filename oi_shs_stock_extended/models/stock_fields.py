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

    def action_view_inspection(self):
        ins_ids = []
        action = self.env.ref('oi_shs_quality_inspection.action_view_inspection').read()[0]
        ins_search = self.env['quality.inspection'].search([('picking_id','=',self.id)])
        for data in ins_search:
            ins_ids.append(data.id)
        action['domain'] = [('id','in',ins_ids)]
        return action


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
    
    
        
