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
            "Receipt Date", "Customer Reference (e-way bill)", "Receipt Status", 
            "Receipt Qty (Done)", "Supply No", "Supply Date", "Customer Reference (e-way bill)", 
            "Supply Status", "Supply Product", "Supply Qty"
        ]
        
        row, col = 1, 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1
        row += 1
        
        # Get all purchase orders within the date range
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        for po in purchases:
            if self.from_date <= po.date_approve.date() <= self.to_date:
                pickings = po.order_line.move_ids
                moves_subcontracted = po.order_line.move_ids.filtered(lambda m: m.is_subcontract)
                subcontracted_productions = moves_subcontracted.move_orig_ids.production_id
                subcontracts = subcontracted_productions.picking_ids
                
                # Write PO details at the start of each purchase order
                col = 0
                worksheet.write(row, col, str(po.name), style_normal)
                col += 1
                worksheet.write(row, col, str(po.partner_id.name), style_normal)
                col += 1
                worksheet.write(row, col, str(po.date_order.strftime('%d/%m/%Y')), style_normal)
                col += 1

                for pol in po.order_line:
                    col = 3
                    worksheet.write(row, col, str(pol.product_id.name), style_normal)
                    col += 1
                    worksheet.write(row, col, str(pol.product_qty), style_normal)
                    col += 1
                    
                    # Filter pickings for the current product
                    pick = pickings.filtered(lambda m: m.product_id == pol.product_id)
                    
                    # Iterate through pickings and write the done quantities separately
                    for val in pick:
                        col = 5
                        worksheet.write(row, col, str(val.picking_id.name), style_normal)  # Receipt No
                        col += 1
                        worksheet.write(row, col, val.picking_id.date_done.strftime('%d/%m/%Y') if val.picking_id.date_done else '', style_normal)  # Receipt Date
                        col += 1
                        worksheet.write(row, col, val.picking_id.customer_reference or '', style_normal)  # Customer Reference (e-way bill)
                        col += 1

                        # Write the "Receipt Status"
                        state = {
                            'draft': 'Draft',
                            'waiting': 'Waiting for another Operation',
                            'confirmed': 'Waiting',
                            'assigned': 'Ready',
                            'done': 'Done',
                            'cancel': 'Cancel'
                        }.get(val.picking_id.state, 'Unknown')
                        worksheet.write(row, col, state, style_normal)
                        col += 1

                        # Write the separate done quantity for the picking
                        worksheet.write(row, col, str(val.quantity_done), style_normal)  # Receipt Qty (Done)
                        col += 1

                        # Process subcontracted information if any
                        link = pick._get_subcontract_production().move_raw_ids
                        supply = []
                        for sub in subcontracts:
                            if sub.origin == val.picking_id.name:
                                sub_lines = sub.move_ids_without_package.filtered(lambda m: m.move_dest_ids.ids)
                                for sl in sub.move_ids_without_package:
                                    for b in sl.move_dest_ids:
                                        if b.id in link.ids:
                                            if sl.picking_id.name not in supply:
                                                supply.append(sl.picking_id.name)
                                                col = 10
                                                worksheet.write(row, col, str(sl.picking_id.name), style_normal)  # Supply No
                                                col += 1

                                                # Write the "Supply Date"
                                                worksheet.write(row, col, sl.picking_id.date_done.strftime('%d/%m/%Y') if sl.picking_id.date_done else '', style_normal)
                                                col += 1
                                                worksheet.write(row, col, sl.picking_id.customer_reference or '', style_normal)  # Customer Reference (e-way bill)
                                                col += 1

                                                # Write "Supply Status"
                                                state = {
                                                    'draft': 'Draft',
                                                    'waiting': 'Waiting for another Operation',
                                                    'confirmed': 'Waiting',
                                                    'assigned': 'Ready',
                                                    'done': 'Done',
                                                    'cancel': 'Cancel'
                                                }.get(sl.picking_id.state, 'Unknown')
                                                worksheet.write(row, col, state, style_normal)
                                                col += 1

                                                # Write "Supply Product"
                                                worksheet.write(row, col, str(sl.product_id.name), style_normal)
                                                col += 1

                                                # Write "Supply Quantity"
                                                worksheet.write(row, col, str(sl.quantity_done), style_normal)
                                                col += 1
                                                
                        row += 1  # Move to the next row after processing all pickings for this product line

                row += 1  # Add empty row after finishing the order
                
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

