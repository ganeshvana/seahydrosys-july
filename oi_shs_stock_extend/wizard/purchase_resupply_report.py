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
                        
                        pick = pickings.filtered(lambda m: m.product_id == pol.product_id)
            if pick:
                total_receipt_qty = sum(p.quantity_done for p in pick)
                
                for val in pick:
                    col = 5
                    worksheet.write(row, col, str(val.picking_id.name), style_normal)
                    col += 1

                    # For "Receipt Date" - Format to show only the date
                    worksheet.write(row, col, val.picking_id.date_done.strftime('%d/%m/%Y') if val.picking_id.date_done else '', style_normal)
                    col += 1

                    worksheet.write(row, col, val.picking_id.customer_reference or '', style_normal)  # Customer Reference (e-way bill)
                    col += 1

                    # Handle different states
                    state = dict(val.picking_id._fields['state'].selection).get(val.picking_id.state, '')
                    worksheet.write(row, col, state, style_normal)
                    col += 1

                    # Receipt Quantity
                    worksheet.write(row, col, str(total_receipt_qty), style_normal)
                    col += 1

                    # Handle subcontract pickings
                    subcontracts = subcontracts.filtered(lambda s: s.origin == val.picking_id.name)
                    if subcontracts:
                        for sub in subcontracts:
                            subcontract_moves = sub.move_ids_without_package.filtered(lambda m: m.move_dest_ids)
                            
                            # Link to the original move
                            linked_moves = pick._get_subcontract_production().move_raw_ids
                            for sl in subcontract_moves:
                                if any(dest.id in linked_moves.ids for dest in sl.move_dest_ids):
                                    col = 10
                                    
                                    # Write Supply Picking Information
                                    worksheet.write(row, col, str(sl.picking_id.name), style_normal)
                                    col += 1
                                    
                                    # For "Supply Date" - Format to show only the date
                                    worksheet.write(row, col, sl.picking_id.date_done.strftime('%d/%m/%Y') if sl.picking_id.date_done else '', style_normal)
                                    col += 1

                                    worksheet.write(row, col, sl.picking_id.customer_reference or '', style_normal)  # Customer Reference (e-way bill)
                                    col += 1

                                    # Handle different states for supply
                                    state = dict(sl.picking_id._fields['state'].selection).get(sl.picking_id.state, '')
                                    worksheet.write(row, col, state, style_normal)
                                    col += 1

                                    # Supply Product
                                    worksheet.write(row, col, str(sl.product_id.name), style_normal)
                                    col += 1

                                    # Supply Quantity
                                    worksheet.write(row, col, str(sl.quantity_done), style_normal)
                                    col += 1

                                    row += 1

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
