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

    # def _action_done(self):
    #     """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
    #     This method makes sure every `stock.move.line` is linked to a `stock.move` by either
    #     linking them to an existing one or a newly created one.

    #     If the context key `cancel_backorder` is present, backorders won't be created.

    #     :return: True
    #     :rtype: bool
    #     """
    #     self._check_company()

    #     todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
    #     for picking in self:
    #         if picking.owner_id:
    #             picking.move_lines.write({'restrict_partner_id': picking.owner_id.id})
    #             picking.move_line_ids.write({'owner_id': picking.owner_id.id})
    #     todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
    #     self.write({'date_done': fields.Datetime.now(), 'priority': '0'})

    #     # if incoming moves make other confirmed/partially_available moves available, assign them
    #     done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines.filtered(lambda m: m.state == 'done')
    #     done_incoming_moves._trigger_assign()

    #     self._send_confirmation_email()
    #     return True
        
    supplier_ref = fields.Char(string="Supplier's Ref")
    drawing_no = fields.Char(string='Drawing No.')
    motor_vehicle_no = fields.Char(string="Motor Vehicle No")
    duration_of_process = fields.Char(string="Duration of Process")
    nature_of_process = fields.Char(string="Nature of Process")
    destination = fields.Char(string='Destination')
    despatched_through = fields.Char('Despatched Through')
    buyer_order_no = fields.Char(string="Buyer's Order No")
    customer_reference = fields.Char(string="Customer Reference")
   
  

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
    
    
        
