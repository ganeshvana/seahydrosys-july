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

    # def action_view_inspection(self):
    #     ins_ids = []
    #     action = self.env.ref('oi_shs_quality_inspection.action_view_inspection').read()[0]
    #     ins_search = self.env['quality.inspection'].search([('picking_id','=',self.id)])
    #     for data in ins_search:
    #         ins_ids.append(data.id)
    #     action['domain'] = [('id','in',ins_ids)]
    #     return action

    def action_view_inspection(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("oi_shs_quality_inspection.action_view_inspection")
        ins_search = self.env['quality.inspection'].search([('picking_id', '=', self.id)])
        action['domain'] = [('id', 'in', ins_search.ids)]
        action['context'] = dict(self._context, create=False)
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
    vendor = fields.Many2one('res.partner',string='Partner',compute='_get_partner')

    @api.depends('origin')
    def _get_partner(self):
        for record in self:
            record.vendor = ''
            if record.picking_type_id.code == 'internal':
                pur_obj = self.env['purchase.order'].search([('name','=',record.origin)])
                if pur_obj:
                    record.vendor = pur_obj.partner_id
                else:
                    record.vendor = ''
  
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
    
    
        
