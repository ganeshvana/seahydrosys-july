# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Picking(models.Model):
    _inherit = 'stock.picking'

    scheduled_date = fields.Datetime(
        'Scheduled Date',
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves."
    )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    po_date = fields.Date("Purchase Order Date")

    # add stock move value
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if self.po_date:
            for re in res:
                re['date'] = self.po_date.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
                re['date_deadline'] = self.po_date.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
        return res

    def _create_stock_moves(self, picking):
        values = []
        for line in self.filtered(lambda l: not l.display_type):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # create picking values
    @api.model
    def _prepare_picking_vals(self, purchase_line_id):
        self.group_id = {}
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(
                _("You must set a Vendor Location for this partner %s") % self.partner_id.name)

        if purchase_line_id.po_date:
            return {
                'picking_type_id': self.picking_type_id.id,
                'partner_id': self.partner_id.id,
                'user_id': False,
                'date': purchase_line_id.po_date,
                'origin': self.name,
                'location_dest_id': self._get_destination_location(),
                'location_id': self.partner_id.property_stock_supplier.id,
                'company_id': self.company_id.id,
            }

        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }

    # search condition in picking
    def _search_picking_for_assignation(self, purchase_line_id):
        self.ensure_one()
        if purchase_line_id.po_date:
            picking = self.env['stock.picking'].search([
                ('picking_type_id', '=', self.picking_type_id.id),
                ('partner_id', '=', self.partner_id.id),
                ('scheduled_date', '=', purchase_line_id.po_date),
                ('origin', '=', self.name),
                ('company_id', '=', self.company_id.id),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
        else:
            picking = self.env['stock.picking'].search([
                ('picking_type_id', '=', self.picking_type_id.id),
                ('partner_id', '=', self.partner_id.id),
                ('scheduled_date', '=', purchase_line_id.date_order),
                ('origin', '=', self.name),
                ('company_id', '=', self.company_id.id),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
        return picking

    def _create_picking(self):
        stock_picking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(
                    lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    for line in order.order_line:
                        picking = self._search_picking_for_assignation(line)
                        if not picking:
                            res = order._prepare_picking_vals(line)
                            picking = stock_picking.create(res)
                        moves = line._create_stock_moves(picking)
                        moves = moves.filtered(lambda x: x.state not in (
                            'done', 'cancel'))._action_confirm()
                        seq = 0
                        for move in sorted(moves, key=lambda move: move.date_deadline):
                            seq += 5
                            move.sequence = seq
                        moves._action_assign()
                        picking.message_post_with_view(
                            'mail.message_origin_link',
                            values={
                                'self': picking, 'origin': order
                            },
                            subtype_id=self.env.ref('mail.mt_note').id)
                else:
                    picking = pickings[0]

        return True


class StockMove(models.Model):
    _inherit = 'stock.move'

    date_deadline = fields.Datetime(
        "Deadline", readonly=True,
        help="Date Promise to the customer on the top level document (SO/PO)")
