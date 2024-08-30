import base64
import io
from odoo import models, fields
import xlsxwriter

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
        
        # Headers
        headers = [
            "PO No:",
            "Vendor",
            "Date",
            "Product",
            "Order Qty",
            "Receipt No",
            "Receipt Date",
            "Receipt Status",
            "Receipt Qty",
            "Supply No",
            "Supply Date",
            "Supply Status",
            "Supply Product",
            "Supply Qty",
        ]
        
        row = 0
        col = 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1       
        row += 1
        
        # Fetch purchase orders
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        for po in purchases:
            if self.from_date <= po.date_approve.date() <= self.to_date:
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
                    
                    # Find stock pickings related to the order line
                    pickings = pol.move_ids.filtered(lambda m: m.picking_id)
                    for picking in pickings:
                        col = 5
                        worksheet.write(row, col, str(picking.picking_id.name), style_normal)
                        col += 1
                        # Get the state of the picking
                        state = dict(picking.picking_id._fields['state'].selection).get(picking.picking_id.state, 'Unknown')
                        worksheet.write(row, col, str(state), style_normal)
                        col += 1
                        worksheet.write(row, col, str(picking.quantity_done), style_normal)
                        col += 1
                        # Retrieve and write the receipt date (date_done) from the picking
                        receipt_date = picking.picking_id.date_done
                        worksheet.write(row, col, str(receipt_date.strftime('%d/%m/%Y') if receipt_date else 'N/A'), style_normal)
                        col += 1
                        
                        # Handle supply details
                        link = picking._get_subcontract_production().move_raw_ids
                        supply = []
                        for sub in picking.picking_id.move_ids_without_package:
                            if sub.picking_id.name not in supply:
                                supply.append(sub.picking_id.name)
                                col = 8
                                worksheet.write(row, col, str(sub.picking_id.name), style_normal)
                                col += 1
                                state = dict(sub.picking_id._fields['state'].selection).get(sub.picking_id.state, 'Unknown')
                                worksheet.write(row, col, str(state), style_normal)
                                col += 1
                                worksheet.write(row, col, str(sub.product_id.name), style_normal)
                                col += 1
                                worksheet.write(row, col, str(sub.quantity_done), style_normal)
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
