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
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round



class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    # po_id = fields.Many2one('purchase.order','PO Number')

    # @api.multi
    # def button_validate(self):
    #     self.ensure_one()
    #     precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     if self.picking_type_id.id == 2:
    #         if self.production_id:
    #             mo_obj = self.env['mrp.production'].search([('id','=',self.production_id.id)])
    #             for line in mo_obj.move_raw_ids:
    #                 move_obj=self.env['stock.move'].search([('product_id','=',line.product_id.id),('picking_id','=',self.id)])
    #                 qty_done = 0
    #                 for move_line in move_obj.move_line_ids:
                        
    #                     qty_done += move_line.qty_done
    #                 if move_obj:                   
    #                     if qty_done != line.product_uom_qty:
    #                         raise UserError(_('Qty does not match with MO qty'))
                            
    #                 if move_obj == False:
    #                     raise UserError(_('No relevant product found in MO'))


    #     if not self.move_lines and not self.move_line_ids:
    #         raise UserError(_('Please add some items to move.'))

    #     picking_type = self.picking_type_id
    #     precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids)
    #     no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
    #     if no_reserved_quantities and no_quantities_done:
    #         raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        
    #     if picking_type.use_create_lots or picking_type.use_existing_lots:
    #         lines_to_check = self.move_line_ids
    #         if not no_quantities_done:
    #             lines_to_check = lines_to_check.filtered(
    #                 lambda line: float_compare(line.qty_done, 0,
    #                                            precision_rounding=line.product_uom_id.rounding)
    #             )

    #         for line in lines_to_check:
    #             product = line.product_id
    #             if product and product.tracking != 'none':
    #                 if not line.lot_name and not line.lot_id:
    #                     raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

    #     if no_quantities_done:
    #         view = self.env.ref('stock.view_immediate_transfer')
    #         wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
    #         return {
    #             'name': _('Immediate Transfer?'),
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'stock.immediate.transfer',
    #             'views': [(view.id, 'form')],
    #             'view_id': view.id,
    #             'target': 'new',
    #             'res_id': wiz.id,
    #             'context': self.env.context,
    #         }

    #     if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
    #         view = self.env.ref('stock.view_overprocessed_transfer')
    #         wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'stock.overprocessed.transfer',
    #             'views': [(view.id, 'form')],
    #             'view_id': view.id,
    #             'target': 'new',
    #             'res_id': wiz.id,
    #             'context': self.env.context,
    #         }

        
    #     if self._check_backorder():
    #         return self.action_generate_backorder_wizard()
    #     self.action_done()
    #     return

    # def action_generate_backorder_wizard(self):
    #     view = self.env.ref('stock.view_backorder_confirmation')
    #     wiz = self.env['stock.backorder.confirmation'].create({'pick_ids': [(4, p.id) for p in self]})
    #     return {
    #         'name': _('Create Backorder?'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'stock.backorder.confirmation',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': wiz.id,
    #         'context': self.env.context,
    #     }
        
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    categ_id = fields.Many2one(related='product_id.categ_id',store=True, string="Product Category")
    weight = fields.Float(related='product_id.weight',string="weight in (kg)" store=True)
    total_weight = fields.Float("Total",compute='compute_total_weight', store=True)
    lot_qty = fields.Float(related='lot_id.product_qty')
    
    @api.depends('qty_done', 'weight')
    def compute_total_weight(self):
        for rec in self:
            rec.total_weight = rec.weight * rec.qty_done
            
    def process_gap(self):
        for rec in self.env['stock.move.line'].search([('categ_id', '=', False)]):
            rec.categ_id = rec.product_id.categ_id.id
            rec.weight = rec.product_id.weight
            rec.total_weight = rec.product_id.weight * rec.qty_done
            self.env.cr.commit()
        

            
# class purchase_order_extend(models.Model):
#     _inherit = 'purchase.order'

#     # pick_id = fields.Many2one('stock.picking','DO')


#     @api.multi
#     def button_confirm(self):
#         for order in self:
#             if self.origin:
#                 mo_obj = self.env['mrp.production'].search([('name', '=', self.origin)])
#                 if mo_obj:
#                     for line in mo_obj.move_raw_ids:
#                         for po_line in self.order_line:
#                             if line.product_id == po_line.product_id:
#                                 if po_line.product_qty > line.product_uom_qty:
#                                     raise UserError(_('PO Qty does not match with MO qty'))

#             if order.state not in ['draft', 'sent']:
#                 continue
#             order._add_supplier_to_product()
#             if order.company_id.po_double_validation == 'one_step'\
#                     or (order.company_id.po_double_validation == 'two_step'\
#                         and order.amount_total < self.env.user.company_id.currency_id._convert(
#                             order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
#                     or order.user_has_groups('purchase.group_purchase_manager'):
#                 order.button_approve()
#             else:
#                 order.write({'state': 'to approve'})
#         return True
  


  




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
