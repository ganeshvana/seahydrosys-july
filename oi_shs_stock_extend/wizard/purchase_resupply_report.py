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
                pickings = po.picking_ids.filtered(lambda p: p.state == 'done')  
                subcontracted_productions = po.order_line.mapped('move_ids').mapped('move_orig_ids.production_id.picking_ids')

                col = 0
                worksheet.write(row, col, str(po.name), style_normal)
                col += 1
                worksheet.write(row, col, str(po.partner_id.name), style_normal)
                col += 1
                worksheet.write(row, col, str(po.date_order.strftime('%d/%m/%Y')), style_normal)
                col += 1
                
                for pol in po.order_line:
                 
                    worksheet.write(row, col, str(pol.product_id.name), style_normal)
                    col += 1
                    worksheet.write(row, col, str(pol.product_qty), style_normal)
                    col += 1
                    
                    pick = pickings.filtered(lambda p: pol.product_id in p.move_lines.mapped('product_id'))
                    if pick:
                      
                        total_receipt_qty = sum(pick.move_lines.filtered(lambda m: m.product_id == pol.product_id).mapped('quantity_done'))
                        for p in pick:
                            col = 5
                            worksheet.write(row, col, str(p.name), style_normal)  
                            col += 1
                            worksheet.write(row, col, p.date_done.strftime('%d/%m/%Y') if p.date_done else '', style_normal)  
                            col += 1
                            worksheet.write(row, col, p.customer_reference or '', style_normal)  
                            col += 1

                            state_mapping = {
                                'draft': 'Draft',
                                'waiting': 'Waiting for another Operation',
                                'confirmed': 'Waiting',
                                'assigned': 'Ready',
                                'done': 'Done',
                                'cancel': 'Cancel'
                            }
                            worksheet.write(row, col, state_mapping.get(p.state, ''), style_normal)  
                            col += 1
                            worksheet.write(row, col, str(total_receipt_qty), style_normal) 
                            col += 1

                          
                            subcontract_moves = subcontracted_productions.filtered(lambda sub: sub.origin == p.name).mapped('move_lines')
                            for sub_move in subcontract_moves:
                                worksheet.write(row, col, str(sub_move.picking_id.name), style_normal) 
                                col += 1
                                worksheet.write(row, col, sub_move.picking_id.date_done.strftime('%d/%m/%Y') if sub_move.picking_id.date_done else '', style_normal)  
                                col += 1
                                worksheet.write(row, col, sub_move.picking_id.customer_reference or '', style_normal)  
                                col += 1

                                state = state_mapping.get(sub_move.picking_id.state, '')
                                worksheet.write(row, col, state, style_normal)  
                                col += 1

                                worksheet.write(row, col, str(sub_move.product_id.name), style_normal) 
                                col += 1
                                worksheet.write(row, col, str(sub_move.quantity_done), style_normal)  
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

