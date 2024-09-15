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

        # Define styles
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'left'})

        # Define headers
        headers = [
            "PO No:", "Vendor", "Date", "Product", "Order Qty", "Receipt No", 
            "Receipt Date", "Customer Reference(e-way bill)", "Receipt Status", 
            "Receipt Qty", "Supply No", "Supply Date", "Supply Reference", 
            "Supply Status", "Supply Product", "Supply Qty"
        ]
        
        # Write headers
        row, col = 1, 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1

        row += 1
        
        # Search and filter purchase orders within the date range
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        filtered_po = purchases.filtered(lambda po: self.from_date <= po.date_approve.date() <= self.to_date)
        
        for po in filtered_po:
            pickings = po.order_line.move_ids.filtered(lambda m: m.state == 'done')
            subcontract_picks = po.order_line.move_ids.filtered(lambda m: m.is_subcontract).mapped('move_orig_ids.production_id.picking_ids')

            for line in po.order_line:
                product_picks = pickings.filtered(lambda p: p.product_id == line.product_id)
                if not product_picks:
                    continue  # Skip if no picking is found for the product

                # Write PO, vendor, and order details
                worksheet.write(row, 0, po.name, style_normal)
                worksheet.write(row, 1, po.partner_id.name, style_normal)
                worksheet.write(row, 2, po.date_order.strftime('%d/%m/%Y'), style_normal)
                worksheet.write(row, 3, line.product_id.name, style_normal)
                worksheet.write(row, 4, line.product_qty, style_normal)

                for pick in product_picks:
                    col = 5
                    worksheet.write(row, col, pick.picking_id.name, style_normal)
                    worksheet.write(row, col + 1, pick.picking_id.date_done.strftime('%d/%m/%Y') if pick.picking_id.date_done else '', style_normal)
                    worksheet.write(row, col + 2, pick.picking_id.customer_reference or '', style_normal)

                    # Status handling
                    status_map = {
                        'draft': 'Draft',
                        'waiting': 'Waiting for another Operation',
                        'confirmed': 'Waiting',
                        'assigned': 'Ready',
                        'done': 'Done',
                        'cancel': 'Cancel'
                    }
                    worksheet.write(row, col + 3, status_map.get(pick.picking_id.state, ''), style_normal)
                    worksheet.write(row, col + 4, pick.quantity_done, style_normal)

                    # Check subcontracted supplies
                    relevant_subcontract_picks = subcontract_picks.filtered(lambda s: s.origin == pick.picking_id.name)
                    for subcontract in relevant_subcontract_picks:
                        col = 10
                        worksheet.write(row, col, subcontract.name, style_normal)
                        worksheet.write(row, col + 1, subcontract.date_done.strftime('%d/%m/%Y') if subcontract.date_done else '', style_normal)
                        worksheet.write(row, col + 2, subcontract.customer_reference or '', style_normal)
                        worksheet.write(row, col + 3, status_map.get(subcontract.state, ''), style_normal)

                        # Subcontract product and quantity
                        for sub_line in subcontract.move_ids_without_package:
                            worksheet.write(row, col + 4, sub_line.product_id.name, style_normal)
                            worksheet.write(row, col + 5, sub_line.quantity_done, style_normal)

                        row += 1
                    row += 1
                row += 1

        # Close the workbook and return data
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

