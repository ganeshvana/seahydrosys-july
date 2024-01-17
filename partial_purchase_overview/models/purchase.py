# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_order_open = fields.Boolean(compute="_compute_is_order_open_reception_status", store=True,tracking=True)
    reception_status = fields.Selection([
        ('done', 'Done'), ('partiall_delivered', 'Partially Delivered'), ('force_closure', 'Force Closure')
    ], compute='_compute_is_order_open_reception_status', store=True,tracking=True)

    @api.depends('order_line', 'order_line.qty_received', 'order_line.product_qty')
    def _compute_is_order_open_reception_status(self):
        for order in self:
            total_ordered_qty = sum(order.order_line.mapped('product_qty'))
            total_received_qty = sum(order.order_line.mapped('qty_received'))
            undelivered_products = any([line.undelivered_products for line in order.order_line])
            partial_qty_to_receive = any([line.partial_qty_to_receive for line in order.order_line])
            if total_ordered_qty == total_received_qty:
                order.reception_status = 'done'
            elif partial_qty_to_receive:
                order.reception_status = 'partiall_delivered'
            elif undelivered_products:
                order.reception_status = 'force_closure'
            order.is_order_open = total_received_qty < total_ordered_qty


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    partial_qty_to_receive = fields.Float(
        compute="_compute_partial_qty_to_receive", digits='Product Unit of Measure', store=True,
        help="Total product qauntities from all open back orders",tracking=True)
    pending_qty = fields.Float(
        compute="_compute_pending_qty", digits='Product Unit of Measure', store=True,
        help="By considering Back order and cancelled backorder and 'No back order'",tracking=True)
    undelivered_products = fields.Boolean(compute="_compute_partial_qty_to_receive", store=True,tracking=True)
    is_order_open = fields.Boolean(related='order_id.is_order_open',tracking=True)
    order_reception_status = fields.Selection(related="order_id.reception_status",tracking=True)

    @api.depends('product_qty', 'qty_received')
    def _compute_pending_qty(self):
        for line in self:
            line.pending_qty = line.product_qty - line.qty_received

    @api.depends('move_ids', 'move_ids.state')
    def _compute_partial_qty_to_receive(self):
        for line in self:
            partial_qty_to_receive = sum(line.move_ids.filtered(
                lambda m: m.state not in ('done', 'cancel')).mapped('product_uom_qty'))
            line.partial_qty_to_receive = partial_qty_to_receive
            line.undelivered_products = line.product_qty != line.pending_qty and not partial_qty_to_receive
