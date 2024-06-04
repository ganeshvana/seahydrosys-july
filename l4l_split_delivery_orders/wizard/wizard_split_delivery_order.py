# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LeapSplitDeliveryOrder(models.TransientModel):
    _name = 'leap.split.delivery.order'
    _description = 'Create Wizard For Split Delivery Order'

    split_delivery_lines = fields.One2many('leap.split.delivery.order.line', 'split_delivery_id')

    def button_action_split_delivery_order(self):
        if not self.split_delivery_lines:
            raise ValidationError(f"There is no Line to Split Transfer in Order.")
        delivery_ids = self.split_delivery_lines.line_id.picking_id
        delivery_id = delivery_ids.copy()
        delivery_id.stock_id = delivery_ids and delivery_ids.id or False
        delivery_id.move_ids_without_package.unlink()

        for line in self.split_delivery_lines:
            delivery_line_id = line.line_id.copy({'picking_id': delivery_id.id})
            delivery_line_id.product_uom_qty = line.demand
            if line.demand > line.line_id.product_uom_qty:
                raise ValidationError(
                    f"Quantity of Demand {line.line_id.product_id.name} cannot exceed {line.line_id.product_uom_qty}.")
            elif line.demand == 0:
                delivery_line_id.unlink()
            elif line.demand == line.line_id.product_uom_qty:
                line.line_id.product_uom_qty = 0
                stock_moves_to_delete = self.env['stock.move'].search([('product_uom_qty', '=', 0)])
                move_ids_to_delete = stock_moves_to_delete.ids
                query = """DELETE FROM stock_move WHERE product_uom_qty = 0"""
                self._cr.execute(query, (tuple(move_ids_to_delete),))
            elif line.demand < line.line_id.product_uom_qty:
                line.line_id.product_uom_qty -= line.demand
        action = self.env['ir.actions.actions']._for_xml_id('stock.action_picking_tree_all')

        if len(delivery_id) > 1:
            action['domain'] = [('id', 'in', delivery_id.ids)]
        elif len(delivery_id) == 1:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]

            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view

            action['res_id'] = delivery_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
            return action
        return action


class LeapSplitDeliveryOrderLine(models.TransientModel):
    _name = 'leap.split.delivery.order.line'
    _description = 'Wizard for Split Delivery Order Line'

    split_delivery_id = fields.Many2one('leap.split.delivery.order', string='Order Id', ondelete='cascade')
    line_id = fields.Many2one(comodel_name='stock.move')
    product_id = fields.Many2one(string="Product", comodel_name='product.product', ondelete='restrict')
    demand = fields.Float(string="Demand")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
