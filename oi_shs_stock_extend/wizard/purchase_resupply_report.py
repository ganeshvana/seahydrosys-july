from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from datetime import datetime
import io
from odoo.tools.misc import xlsxwriter

class ResupplyReport(models.TransientModel):
    _name = 'resupply.report'

    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()

    def fuel_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Resupply')
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'left'})
        
        headers = [
            "PO No:", "Vendor", "Date", "Product", "Order Qty", "Receipt No", 
            "Receipt Date", "Customer Reference (e-way bill)", "Receipt Status", "Receipt Qty", 
            "Supply No", "Supply Date", "Customer Reference (e-way bill)", "Supply Status", 
            "Supply Product", "Supply Qty"
        ]
        
        # Write header
        row, col = 1, 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1
        row += 1
        
        # Fetching the purchase orders in 'purchase' or 'done' state
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        for po in purchases:
            if self.from_date <= po.date_approve.date() <= self.to_date:
                pickings = po.picking_ids  # Fetch all receipts (stock pickings) for the purchase order
                
                # Loop through each product line of the purchase order
                for pol in po.order_line:
                    col = 0
                    worksheet.write(row, col, str(po.name), style_normal)
                    col += 1
                    worksheet.write(row, col, str(po.partner_id.name), style_normal)
                    col += 1
                    worksheet.write(row, col, str(po.date_order.strftime('%d/%m/%Y')), style_normal)
                    col += 1
                    worksheet.write(row, col, str(pol.product_id.name), style_normal)
                    col += 1
                    worksheet.write(row, col, str(pol.product_qty), style_normal)
                    col += 1
                    
                    # Loop through each receipt (stock picking) for the product line
                    for picking in pickings.filtered(lambda p: p.state == 'done'):
                        move_lines = picking.move_lines.filtered(lambda m: m.product_id == pol.product_id)
                        
                        for move in move_lines:
                            col = 5
                            worksheet.write(row, col, str(picking.name), style_normal)  # Receipt No
                            col += 1

                            # For "Receipt Date" - Format to show only the date
                            worksheet.write(row, col, picking.date_done.strftime('%d/%m/%Y') if picking.date_done else '', style_normal)
                            col += 1
                            worksheet.write(row, col, picking.customer_reference or '', style_normal)  # Customer Reference (e-way bill)
                            col += 1

                            # Determine the receipt state
                            state = 'Done' if picking.state == 'done' else 'Cancel'
                            worksheet.write(row, col, state, style_normal)
                            col += 1

                            # Write the receipt quantity (0.0 if the state is 'cancel')
                            qty_done = move.quantity_done if picking.state != 'cancel' else 0.0
                            worksheet.write(row, col, str(qty_done), style_normal)
                            col += 1
                            
                            # Fetch supply details (if applicable)
                            subcontracts = move._get_subcontract_production().picking_ids
                            for sub in subcontracts:
                                if sub.origin == picking.name:
                                    worksheet.write(row, col, str(sub.name), style_normal)
                                    col += 1
                                    worksheet.write(row, col, sub.date_done.strftime('%d/%m/%Y') if sub.date_done else '', style_normal)
                                    col += 1
                                    worksheet.write(row, col, sub.customer_reference or '', style_normal)  # Customer Reference (e-way bill) for subcontract
                                    col += 1

                                    # Determine the supply state
                                    supply_state = 'Done' if sub.state == 'done' else 'Cancel'
                                    worksheet.write(row, col, supply_state, style_normal)
                                    col += 1

                                    # Supply Product
                                    worksheet.write(row, col, str(sub.move_lines[0].product_id.name), style_normal)
                                    col += 1

                                    # Supply Quantity
                                    worksheet.write(row, col, str(sub.move_lines[0].quantity_done), style_normal)
                                    col += 1
                                    row += 1
                    row += 1
        
        workbook.close()
        xlsx_data = output.getvalue()
        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "Resupply.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
