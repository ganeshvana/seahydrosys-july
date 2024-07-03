# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vishnuraj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models, _


class StockPicking(models.Model):
    """
    Inherit Pickings class for add merge orders action function,
    Method:
         action_merge_picking(self):
            Create new wizard with selected records
    """
    _inherit = 'stock.picking'

    def action_merge_picking(self):
        """ Method create wizard for select pickings """
        merge_picking = self.env['merge.picking'].create({
            'merge_picking_ids': [fields.Command.set(self.ids)],
        })
        return {
            'name': _('Merge Picking Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'merge.picking',
            'view_mode': 'form',
            'res_id': merge_picking.id,
            'target': 'new'
        }

    # def create(self, vals):
    #     res = super(StockPicking, self).create(vals)
    #     if 'customer_reference' in vals:
    #         for line in res.move_lines:
    #             line.description = vals['customer_reference']
    #     return res

    # def write(self, vals):
    #     res = super(StockPicking, self).write(vals)
    #     if 'customer_reference' in vals:
    #         for order in self:
    #             for line in order.move_lines:
    #                 line.description = vals['customer_reference']
    #     return res


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def _sanity_check(self):
        for batch in self:
            pass



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    customer_reference = fields.Char('Customer Reference')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if 'client_order_ref' in vals:
            for line in res.order_line:
                line.customer_reference = vals['client_order_ref']
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'client_order_ref' in vals:
            for order in self:
                for line in order.order_line:
                    line.customer_reference = vals['client_order_ref']
        return res