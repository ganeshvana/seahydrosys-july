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
            "Receipt Qty", "Supply No", "Supply Date", 
            "Customer Reference (e-way bill)", "Supply Status", "Supply Product", "Supply Qty"
        ]
        
        row, col = 1, 0
        # Write headers
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1
        row += 1
        
        # Search for purchase orders in the 'purchase' or 'done' state
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        
        for po in purchases:
            if self.from_date <= po.date_approve.date() <= self.to_date:
                pickings = po.order_line.move_ids
                moves_subcontracted = po.order_line.move_ids.filtered(lambda m: m.is_subcontract)
                subcontracted_productions = moves_subcontracted.move_orig_ids.production_id
                subcontracts = subcontracted_productions.picking_ids
                
                for pol in po.order_line:
                    col = 0
                    # Write PO-related information
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

                    # Filter picking moves related to this product
                    pick = pickings.filtered(lambda m: m.product_id == pol.product_id)
                    if pick:
                        for val in pick:
                            col = 5  # Reset column for the receipt details
                            
                            # Write Receipt No
                            worksheet.write(row, col, str(val.picking_id.name), style_normal)
                            col += 1

                            # Write Receipt Date
                            worksheet.write(row, col, val.picking_id.date_done.strftime('%d/%m/%Y') if val.picking_id.date_done else '', style_normal)
                            col += 1

                            # Write Customer Reference (e-way bill)
                            worksheet.write(row, col, val.picking_id.customer_reference or '', style_normal)
                            col += 1

                            # Determine and write Receipt Status
                            state = {
                                'draft': 'Draft',
                                'waiting': 'Waiting for another Operation',
                                'confirmed': 'Waiting',
                                'assigned': 'Ready',
                                'done': 'Done',
                                'cancel': 'Cancel'
                            }.get(val.picking_id.state, '')
                            worksheet.write(row, col, state, style_normal)
                            col += 1

                            # Write Receipt Quantity
                            worksheet.write(row, col, str(val.quantity_done), style_normal)
                            col += 1

                            # Link subcontract production moves
                            link = pick._get_subcontract_production().move_raw_ids
                            for sub in subcontracts:
                                if sub.origin == val.picking_id.name:
                                    supply = []
                                    sub_lines = sub.move_ids_without_package.filtered(lambda m: m.move_dest_ids.ids)
                                    for a in sub.move_ids_without_package:
                                        for b in a.move_dest_ids:
                                            if b.id in link.ids and a.picking_id.name not in supply:
                                                supply.append(a.picking_id.name)
                                                col = 10  # Reset column for supply details
                                                
                                                # Write Supply No
                                                worksheet.write(row, col, str(a.picking_id.name), style_normal)
                                                col += 1

                                                # Write Supply Date
                                                worksheet.write(row, col, a.picking_id.date_done.strftime('%d/%m/%Y') if a.picking_id.date_done else '', style_normal)
                                                col += 1

                                                # Write Supply Customer Reference
                                                worksheet.write(row, col, a.picking_id.customer_reference or '', style_normal)
                                                col += 1

                                                # Determine and write Supply Status
                                                supply_state = {
                                                    'draft': 'Draft',
                                                    'waiting': 'Waiting for another Operation',
                                                    'confirmed': 'Waiting',
                                                    'assigned': 'Ready',
                                                    'done': 'Done',
                                                    'cancel': 'Cancel'
                                                }.get(a.picking_id.state, '')
                                                worksheet.write(row, col, supply_state, style_normal)
                                                col += 1

                                                # Write Supply Product
                                                worksheet.write(row, col, str(a.product_id.name), style_normal)
                                                col += 1

                                                # Write Supply Quantity
                                                worksheet.write(row, col, str(a.quantity_done), style_normal)
                                                col += 1

                                                # Increment row for next entry
                                                row += 1
                        row += 1  # Move to next PO line
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
