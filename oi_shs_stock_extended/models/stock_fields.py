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
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

    
# class stock_move_inherit(models.Model):
#     _inherit = 'stock.move'

#     def _get_available_quantity(self, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
#         self.ensure_one()
#         if location_id.should_bypass_reservation():
#             return self.product_qty
#         return self.env['stock.quant']._get_available_quantity(self.product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=None, strict=strict, allow_negative=allow_negative)

#     def _update_reserved_quantity(self, need, available_quantity, location_id, lot_id=None, package_id=None, owner_id=None, strict=True):
#         """ Create or update move lines.
#         """
#         self.ensure_one()

#         if not lot_id:
#             lot_id = self.env['stock.production.lot']
#         if not package_id:
#             package_id = self.env['stock.quant.package']
#         if not owner_id:
#             owner_id = self.env['res.partner']

#         # do full packaging reservation when it's needed
#         if self.product_packaging_id and self.product_id.product_tmpl_id.categ_id.packaging_reserve_method == "full":
#             available_quantity = self.product_packaging_id._check_qty(available_quantity, self.product_id.uom_id, "DOWN")

#         taken_quantity = min(available_quantity, need)

#         # `taken_quantity` is in the quants unit of measure. There's a possibility that the move's
#         # unit of measure won't be respected if we blindly reserve this quantity, a common usecase
#         # is if the move's unit of measure's rounding does not allow fractional reservation. We chose
#         # to convert `taken_quantity` to the move's unit of measure with a down rounding method and
#         # then get it back in the quants unit of measure with an half-up rounding_method. This
#         # way, we'll never reserve more than allowed. We do not apply this logic if
#         # `available_quantity` is brought by a chained move line. In this case, `_prepare_move_line_vals`
#         # will take care of changing the UOM to the UOM of the product.
#         if not strict and self.product_id.uom_id != self.product_uom:
#             taken_quantity_move_uom = self.product_id.uom_id._compute_quantity(taken_quantity, self.product_uom, rounding_method='DOWN')
#             taken_quantity = self.product_uom._compute_quantity(taken_quantity_move_uom, self.product_id.uom_id, rounding_method='HALF-UP')

#         quants = []
#         rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')

#         if self.product_id.tracking == 'serial':
#             if float_compare(taken_quantity, int(taken_quantity), precision_digits=rounding) != 0:
#                 taken_quantity = 0

#         try:
#             with self.env.cr.savepoint():
#                 if not float_is_zero(taken_quantity, precision_rounding=self.product_id.uom_id.rounding):
#                     if location_id == 8:
#                         quants = self.env['stock.quant']._update_reserved_quantity(
#                             self.product_id, location_id, taken_quantity, lot_id=lot_id,
#                             package_id=package_id, owner_id=None, strict=strict
#                         )
#                     else:
#                         quants = self.env['stock.quant']._update_reserved_quantity(
#                             self.product_id, location_id, taken_quantity, lot_id=lot_id,
#                             package_id=package_id, owner_id=None, strict=strict
#                         )
#         except UserError:
#             taken_quantity = 0

#         # Find a candidate move line to update or create a new one.
#         for reserved_quant, quantity in quants:
#             to_update = self.move_line_ids.filtered(lambda ml: ml._reservation_is_updatable(quantity, reserved_quant))
#             if to_update:
#                 uom_quantity = self.product_id.uom_id._compute_quantity(quantity, to_update[0].product_uom_id, rounding_method='HALF-UP')
#                 uom_quantity = float_round(uom_quantity, precision_digits=rounding)
#                 uom_quantity_back_to_product_uom = to_update[0].product_uom_id._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
#             if to_update and float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
#                 to_update[0].with_context(bypass_reservation_update=True).product_uom_qty += uom_quantity
#             else:
#                 if self.product_id.tracking == 'serial':
#                     for i in range(0, int(quantity)):
#                         self.env['stock.move.line'].create(self._prepare_move_line_vals(quantity=1, reserved_quant=reserved_quant))
#                 else:
#                     self.env['stock.move.line'].create(self._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant))
#         return taken_quantity

# class stock_picking_inherit(models.Model):
#     _inherit = 'stock.picking'

#     def action_view_inspection(self):
#         ins_ids = []
#         action = self.env.ref('oi_shs_quality_inspection.action_view_inspection').read()[0]
#         ins_search = self.env['quality.inspection'].search([('picking_id','=',self.id)])
#         for data in ins_search:
#             ins_ids.append(data.id)
#         action['domain'] = [('id','in',ins_ids)]
#         return action

    def _action_done(self):
        """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        for picking in self:
            if picking.owner_id:
                picking.move_lines.write({'restrict_partner_id': picking.owner_id.id})
                picking.move_line_ids.write({'owner_id': picking.owner_id.id})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now(), 'priority': '0'})

        # if incoming moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines.filtered(lambda m: m.state == 'done')
        done_incoming_moves._trigger_assign()

        self._send_confirmation_email()
        return True
        
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
    
    
        
