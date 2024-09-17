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
            pickings = po.order_line.move_ids
            moves_subcontracted = po.order_line.move_ids.filtered(lambda m: m.is_subcontract)
            subcontracted_productions = moves_subcontracted.move_orig_ids.production_id
            subcontracts = subcontracted_productions.picking_ids
            
            if subcontracts:
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
                    
                    # Iterate over each receipt for this order line's product
                    for pick in pickings.filtered(lambda m: m.product_id == pol.product_id):
                        pick_sum = pick.quantity_done  # Individual receipt quantity
                        col = 5
                        worksheet.write(row, col, str(pick.picking_id.name), style_normal)  # Receipt No
                        col += 1
                        worksheet.write(row, col, pick.picking_id.date_done.strftime('%d/%m/%Y') if pick.picking_id.date_done else '', style_normal)  # Receipt Date
                        col += 1
                        worksheet.write(row, col, pick.picking_id.customer_reference or '', style_normal)  # Customer Reference (e-way bill)
                        col += 1
                        
                        # Write Receipt Status and handle 'done' stage separately
                        state = ''
                        if pick.picking_id.state == 'draft':
                            state = 'Draft'
                        elif pick.picking_id.state == 'waiting':
                            state = 'Waiting for another Operation'
                        elif pick.picking_id.state == 'confirmed':
                            state = 'Waiting'
                        elif pick.picking_id.state == 'assigned':
                            state = 'Ready'
                        elif pick.picking_id.state == 'done':
                            state = 'Done'
                        elif pick.picking_id.state == 'cancel':
                            state = 'Cancel'
                            pick_sum = 0.0  # Set receipt quantity to 0.0 for 'cancel' status

                        worksheet.write(row, col, state, style_normal)
                        col += 1
                        worksheet.write(row, col, str(pick_sum), style_normal)  # Receipt Quantity
                        col += 1
                        
                        # For each corresponding subcontract, show its details
                        link = pick._get_subcontract_production().move_raw_ids
                        for sub in subcontracts.filtered(lambda sub: sub.origin == pick.picking_id.name):
                            for sl in sub.move_ids_without_package:
                                col = 10
                                worksheet.write(row, col, str(sl.picking_id.name), style_normal)  # Supply No
                                col += 1
                                worksheet.write(row, col, sl.picking_id.date_done.strftime('%d/%m/%Y') if sl.picking_id.date_done else '', style_normal)  # Supply Date
                                col += 1
                                worksheet.write(row, col, sl.picking_id.customer_reference or '', style_normal)  # Supply e-way bill
                                col += 1

                                # Supply Status
                                supply_state = ''
                                if sl.picking_id.state == 'draft':
                                    supply_state = 'Draft'
                                elif sl.picking_id.state == 'waiting':
                                    supply_state = 'Waiting for another Operation'
                                elif sl.picking_id.state == 'confirmed':
                                    supply_state = 'Waiting'
                                elif sl.picking_id.state == 'assigned':
                                    supply_state = 'Ready'
                                elif sl.picking_id.state == 'done':
                                    supply_state = 'Done'
                                elif sl.picking_id.state == 'cancel':
                                    supply_state = 'Cancel'
                                
                                worksheet.write(row, col, supply_state, style_normal)
                                col += 1
                                worksheet.write(row, col, str(sl.product_id.name), style_normal)  # Supply Product
                                col += 1
                                worksheet.write(row, col, str(sl.quantity_done), style_normal)  # Supply Quantity
                                col += 1
                                
                        row += 1  # Move to the next row after handling each receipt

            row += 1
            col = 0

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
