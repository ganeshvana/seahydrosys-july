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
        
        row, col = 1, 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1
        row += 1

        # Fetch all confirmed or completed purchase orders
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        
        for po in purchases:
            if self.from_date <= po.date_approve.date() <= self.to_date:
                for pol in po.order_line:
                    pickings = pol.move_ids.filtered(lambda m: not m.is_subcontract)  # Filter out subcontract moves
                    subcontracts = pol.move_ids.filtered(lambda m: m.is_subcontract).move_orig_ids.production_id.picking_ids
                    
                    # Write Purchase Order and Order Line details
                    col = 0
                    worksheet.write(row, col, po.name, style_normal)
                    col += 1
                    worksheet.write(row, col, po.partner_id.name, style_normal)
                    col += 1
                    worksheet.write(row, col, po.date_order.strftime('%d/%m/%Y'), style_normal)
                    col += 1
                    worksheet.write(row, col, pol.product_id.name, style_normal)
                    col += 1
                    worksheet.write(row, col, pol.product_qty, style_normal)
                    col += 1

                    # Process Pickings
                    if pickings:
                        for pick in pickings:
                            worksheet.write(row, col, pick.picking_id.name, style_normal)
                            col += 1
                            worksheet.write(row, col, pick.picking_id.date_done.strftime('%d/%m/%Y') if pick.picking_id.date_done else '', style_normal)
                            col += 1
                            worksheet.write(row, col, pick.picking_id.customer_reference or '', style_normal)
                            col += 1
                            receipt_state = pick.picking_id.state.capitalize()
                            worksheet.write(row, col, receipt_state, style_normal)
                            col += 1
                            worksheet.write(row, col, sum(p.quantity_done for p in pickings), style_normal)
                            col += 1

                    # Process Subcontract Pickings
                    if subcontracts:
                        for sub in subcontracts:
                            # Ensure pick and sub are valid
                            if pick and pick.picking_id and sub.origin:
                                # Compare only if both origin and picking_id.name exist
                                if sub.origin == pick.picking_id.name:
                                    col = 10
                                    worksheet.write(row, col, str(sub.name), style_normal)
                                    col += 1

                                    # For "Supply Date" - Format to show only the date
                                    worksheet.write(row, col, sub.date_done.strftime('%d/%m/%Y') if sub.date_done else '', style_normal)
                                    col += 1

                                    worksheet.write(row, col, sub.customer_reference or '', style_normal)  # Customer Reference (e-way bill)

                                    col += 1

                                    # Handle different states for supply
                                    state = sub.state.capitalize() if sub.state else ''
                                    worksheet.write(row, col, state, style_normal)

                                    col += 1

                                    # Write each product and quantity in a new row
                                    for move in sub.move_ids_without_package:
                                        worksheet.write(row, col, str(move.product_id.name), style_normal)  # Write product name
                                        col += 1
                                        worksheet.write(row, col, str(move.quantity_done), style_normal)  # Write quantity done
                                        row += 1  # Move to the next row for the next product
                                        col -= 1  # Reset column to the product column for the next product

                                    row += 1  # Move to the next row after the last product entry

                    

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

