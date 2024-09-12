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
        
        # Set headers
        worksheet.write_row(1, 0, headers, style_highlight)
        worksheet.set_column(0, len(headers) - 1, 16)
        
        row = 2  # Starting row after headers
        
        # Search for purchase orders
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        
        for po in purchases:
            if self.from_date <= po.date_approve.date() <= self.to_date:
                pickings = po.order_line.mapped('move_ids')
                subcontracts = po.order_line.mapped('move_ids').filtered(lambda m: m.is_subcontract).mapped('move_orig_ids.production_id.picking_ids')
                
                # Write purchase order details
                for pol in po.order_line:
                    # Filter pickings for the current product
                    pick = pickings.filtered(lambda m: m.product_id == pol.product_id)
                    if not pick:
                        continue
                    
                    total_receipt_qty = sum(p.quantity_done for p in pick)
                    
                    # Write purchase order, receipt, and subcontract details
                    worksheet.write(row, 0, po.name, style_normal)
                    worksheet.write(row, 1, po.partner_id.name, style_normal)
                    worksheet.write(row, 2, po.date_order.strftime('%d/%m/%Y'), style_normal)
                    worksheet.write(row, 3, pol.product_id.name, style_normal)
                    worksheet.write(row, 4, pol.product_qty, style_normal)

                    for val in pick:
                        # Write receipt details
                        worksheet.write(row, 5, val.picking_id.name, style_normal)
                        worksheet.write(row, 6, val.picking_id.date_done.strftime('%d/%m/%Y') if val.picking_id.date_done else '', style_normal)
                        worksheet.write(row, 7, val.picking_id.customer_reference or '', style_normal)
                        worksheet.write(row, 8, dict(val.picking_id._fields['state'].selection).get(val.picking_id.state, ''), style_normal)
                        worksheet.write(row, 9, total_receipt_qty, style_normal)

                        # Subcontract details if related
                        subcontract = subcontracts.filtered(lambda s: s.origin == val.picking_id.name)
                        if subcontract:
                            sl = subcontract.mapped('move_ids_without_package').filtered(lambda m: m.move_dest_ids)
                            if sl:
                                worksheet.write(row, 10, sl[0].picking_id.name, style_normal)
                                worksheet.write(row, 11, sl[0].picking_id.date_done.strftime('%d/%m/%Y') if sl[0].picking_id.date_done else '', style_normal)
                                worksheet.write(row, 12, sl[0].picking_id.customer_reference or '', style_normal)
                                worksheet.write(row, 13, dict(sl[0].picking_id._fields['state'].selection).get(sl[0].picking_id.state, ''), style_normal)
                                worksheet.write(row, 14, sl[0].product_id.name, style_normal)
                                worksheet.write(row, 15, sl[0].quantity_done, style_normal)
                        
                        row += 1  # Move to the next row after writing all details

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

