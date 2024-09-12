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
            "Receipt Date","Customer Reference(e-way bill)","Receipt Status", "Receipt Qty", "Supply No", 
            "Supply Date","Customer Reference(e-way bill)","Supply Status", "Supply Product", "Supply Qty"
        ]
        
        row, col = 1, 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1
        row += 1
        
        # Loop through each purchase order (PO) that is either in 'purchase' or 'done' state
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])

        # Start iterating through purchase orders and populate the worksheet
        for po in purchases:
            # Ensure the purchase order date is within the user-specified date range
            if self.from_date <= po.date_approve.date() <= self.to_date:
                
                # Get the related picking (receipt) and subcontract pickings
                pickings = po.order_line.move_ids
                moves_subcontracted = po.order_line.move_ids.filtered(lambda m: m.is_subcontract)
                subcontracted_productions = moves_subcontracted.move_orig_ids.production_id
                subcontracts = subcontracted_productions.picking_ids
                
                # Start writing data for the purchase order (PO) details
                col = 0
                worksheet.write(row, col, str(po.name), style_normal)  # PO No
                col += 1
                worksheet.write(row, col, str(po.partner_id.name), style_normal)  # Vendor
                col += 1
                worksheet.write(row, col, str(po.date_order.strftime('%d/%m/%Y')), style_normal)  # PO Date
                col += 1
                
                # For each order line (product) in the purchase order
                for pol in po.order_line:
                    col = 3
                    worksheet.write(row, col, str(pol.product_id.name), style_normal)  # Product Name
                    col += 1
                    worksheet.write(row, col, str(pol.product_qty), style_normal)  # Order Qty
                    col += 1
                    
                    # Check for receipts related to this product in the PO
                    pick = pickings.filtered(lambda m: m.product_id == pol.product_id)
                    if pick:
                        for val in pick:
                            col = 5
                            worksheet.write(row, col, str(val.picking_id.name), style_normal)  # Receipt No
                            col += 1
                            worksheet.write(row, col, val.picking_id.date_done.strftime('%d/%m/%Y') if val.picking_id.date_done else '', style_normal)  # Receipt Date
                            col += 1
                            worksheet.write(row, col, val.picking_id.customer_reference or '', style_normal)  # Customer Reference (e-way bill)
                            col += 1

                            # Get and write receipt status
                            state = ''
                            if val.picking_id.state == 'draft':
                                state = 'Draft'
                            elif val.picking_id.state == 'waiting':
                                state = 'Waiting for another Operation'
                            elif val.picking_id.state == 'confirmed':
                                state = 'Waiting'
                            elif val.picking_id.state == 'assigned':
                                state = 'Ready'
                            elif val.picking_id.state == 'done':
                                state = 'Done'
                            elif val.picking_id.state == 'cancel':
                                state = 'Cancel'
                            
                            worksheet.write(row, col, state, style_normal)  # Receipt Status
                            col += 1
                            
                            # Write the receipt quantity (received quantity)
                            worksheet.write(row, col, str(val.quantity_done), style_normal)  # Receipt Qty
                            col += 1

                            # Now move on to the subcontracted supply details below this part
                            row += 1  # Move to the next row for next PO/line

                            # Continue with subcontract logic below this line...

        
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
