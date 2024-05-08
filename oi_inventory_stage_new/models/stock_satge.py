from odoo import api, fields, models, tools, _
from datetime import date
from datetime import datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError, Warning, ValidationError




class StockPickingStage(models.Model):
    _inherit = "stock.picking"

    is_pc = fields.Boolean('Pc Id')
    show_allocation = fields.Boolean('Show Allocation')
    state = fields.Selection(selection_add=[
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('approved_for_done', 'Approve'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    def action_to_approve(self):
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%% action button %%%%%%%%%%%%%")
        self.write({'state': 'approved_for_done'}) 


    def button_validate_new(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (', '.join(pickings_without_lots.mapped('name')), ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location'].search([('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.id), ('location_id.usage', '!=', 'supplier')]).ids
                if self.env['stock.move'].search([
                        ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                        ('product_qty', '>', 0),
                        ('location_id', 'in', wh_location_ids),
                        ('move_orig_ids', '=', False),
                        ('picking_id', 'not in', self.ids),
                        ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action
        return True

class ProductProduct(models.Model):
    _inherit = 'product.product'
    def _run_fifo_vacuum(self, company=None):
        """Compensate layer valued at an estimated price with the price of future receipts
        if any. If the estimated price is equals to the real price, no layer is created but
        the original layer is marked as compensated.

        :param company: recordset of `res.company` to limit the execution of the vacuum
        """
        self.ensure_one()
        if company is None:
            company = self.env.company
        svls_to_vacuum = self.env['stock.valuation.layer'].sudo().search([
            ('product_id', '=', self.id),
            ('remaining_qty', '<', 0),
            ('stock_move_id', '!=', False),
            ('company_id', '=', company.id),
        ], order='create_date, id')
        if not svls_to_vacuum:
            return

        as_svls = []

        domain = [
            ('company_id', '=', company.id),
            ('product_id', '=', self.id),
            ('remaining_qty', '>', 0),
            ('create_date', '>=', svls_to_vacuum[0].create_date),
        ]
        all_candidates = self.env['stock.valuation.layer'].sudo().search(domain)

        for svl_to_vacuum in svls_to_vacuum:
            # We don't use search to avoid executing _flush_search and to decrease interaction with DB
            candidates = all_candidates.filtered(
                lambda r: r.create_date > svl_to_vacuum.create_date
                or r.create_date == svl_to_vacuum.create_date
                and r.id > svl_to_vacuum.id
            )
            if not candidates:
                break
            qty_to_take_on_candidates = abs(svl_to_vacuum.remaining_qty)
            qty_taken_on_candidates = 0
            tmp_value = 0
            for candidate in candidates:
                qty_taken_on_candidate = min(candidate.remaining_qty, qty_to_take_on_candidates)
                qty_taken_on_candidates += qty_taken_on_candidate

                candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
                value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
                value_taken_on_candidate = candidate.currency_id.round(value_taken_on_candidate)
                new_remaining_value = candidate.remaining_value - value_taken_on_candidate

                candidate_vals = {
                    'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
                    'remaining_value': new_remaining_value
                }
                candidate.write(candidate_vals)
                if not (candidate.remaining_qty > 0):
                    all_candidates -= candidate

                qty_to_take_on_candidates -= qty_taken_on_candidate
                tmp_value += value_taken_on_candidate
                if float_is_zero(qty_to_take_on_candidates, precision_rounding=product.uom_id.rounding):
                    break

            # Get the estimated value we will correct.
            remaining_value_before_vacuum = svl_to_vacuum.unit_cost * qty_taken_on_candidates
            new_remaining_qty = svl_to_vacuum.remaining_qty + qty_taken_on_candidates
            corrected_value = remaining_value_before_vacuum - tmp_value
            svl_to_vacuum.write({
                'remaining_qty': new_remaining_qty,
            })

            # Don't create a layer or an accounting entry if the corrected value is zero.
            if svl_to_vacuum.currency_id.is_zero(corrected_value):
                continue

            corrected_value = svl_to_vacuum.currency_id.round(corrected_value)
            move = svl_to_vacuum.stock_move_id
            vals = {
                'product_id': self.id,
                'value': corrected_value,
                'unit_cost': 0,
                'quantity': 0,
                'remaining_qty': 0,
                'stock_move_id': move.id,
                'company_id': move.company_id.id,
                'description': 'Revaluation of %s (negative inventory)' % move.picking_id.name or move.name,
                'stock_valuation_layer_id': svl_to_vacuum.id,
            }
            vacuum_svl = self.env['stock.valuation.layer'].sudo().create(vals)

            if self.valuation != 'real_time':
                continue
            as_svls.append((vacuum_svl, svl_to_vacuum))

        # If some negative stock were fixed, we need to recompute the standard price.
        product = self.with_company(company.id)
        if product.cost_method == 'average' and not float_is_zero(product.quantity_svl, precision_rounding=self.uom_id.rounding):
            product.sudo().with_context(disable_auto_svl=True).write({'standard_price': product.value_svl / product.quantity_svl})

        self.env['stock.valuation.layer'].browse(x[0].id for x in as_svls)._validate_accounting_entries()

        for vacuum_svl, svl_to_vacuum in as_svls:
            self._create_fifo_vacuum_anglo_saxon_expense_entry(vacuum_svl, svl_to_vacuum)




























