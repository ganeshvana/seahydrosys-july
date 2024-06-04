# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    stock_id = fields.Many2one('stock.picking')
    split_order_count = fields.Char(compute='compute_split_order')

    def open_split_delivery_order(self):
        lines = []
        for line in self.move_ids_without_package:
            lines.append((0, 0, {
                'line_id': line and line.id or False,
                'product_id': line.product_id and line.product_id.id or False,
                'demand': line.product_uom_qty or 0,
            }))
        view_id = self.env.ref('l4l_split_delivery_orders.view_leap_wizard_create_split_delivery_order_form').id
        return {
            'name': 'Split Transfer',
            'view_mode': 'form',
            'res_model': 'leap.split.delivery.order',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_split_delivery_lines': lines},
        }

    def compute_split_order(self):
        for split in self:
            split.split_order_count = self.search_count([('stock_id', '=', split.id)])

    def view_action_split_delivery_orders(self):
        split_delivery_ids = self.search([('stock_id', '=', self.id)]).ids

        action = self.env['ir.actions.actions']._for_xml_id('stock.action_picking_tree_all')

        if len(split_delivery_ids) > 1:
            action['domain'] = [('id', 'in', split_delivery_ids)]
        elif len(split_delivery_ids) == 1:
            form_view = [(self.env.ref('stock.view_picking_form').sudo().id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view

            action['res_id'] = split_delivery_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
            return action
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
