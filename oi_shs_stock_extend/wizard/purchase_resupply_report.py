from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from datetime import datetime, timedelta
import io
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
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'left'})
        
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
        
        row = 1
        col = 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1
        row += 1

        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        for po in purchases:
            if self.from_date <= po.date_approve.date() <= self.to_date:
                moves_subcontracted = po.order_line.move_ids.filtered(lambda m: m.is_subcontract)
                subcontracted_productions = moves_subcontracted.move_orig_ids.production_id
                subcontracts = subcontracted_productions.picking_ids
                pickings = po.order_line.move_ids
                
                if subcontracts:
                    worksheet.write(row, 0, str(po.name), style_normal)
                    worksheet.write(row, 1, str(po.partner_id.name), style_normal)
                    worksheet.write(row, 2, str(po.date_order.strftime('%d/%m/%Y')), style_normal)
                    row += 1
                    
                    for pol in po.order_line:
                        col = 3
                        worksheet.write(row, col, str(pol.product_id.name), style_normal)
                        col += 1
                        worksheet.write(row, col, str(pol.product_qty), style_normal)
                        col += 1
                        worksheet.write(row, col, str(pol.date_done), style_normal)
                        col += 1
                        
                        pick = pickings.filtered(lambda m: m.product_id == pol.product_id)
                        for val in pick:
                            col = 5
                            worksheet.write(row, col, str(val.picking_id.name), style_normal)
                            col += 1
                            
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
                            
                            worksheet.write(row, col, str(val.quantity_done), style_normal)
                            col += 1
                            
                            link = pick._get_subcontract_production().move_raw_ids
                            supply = []
                            for sub in subcontracts:
                                if sub.origin == val.picking_id.name:
                                    at_line = []
                                    sub_lines = sub.move_ids_without_package.filtered(lambda m: m.move_dest_ids.ids)
                                    for a in sub.move_ids_without_package:
                                        for b in a.move_dest_ids:
                                            if b.id in link.ids:
                                                at_line.append(a)
                                    for sl in at_line:
                                        if sl.picking_id.name not in supply:
                                            supply.append(sl.picking_id.name)
                                            col = 8
                                            worksheet.write(row, col, str(sl.picking_id.name), style_normal)
                                            col += 1
                                            
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
                                            
                                            worksheet.write(row, col, str(sl.product_id.name), style_normal)
                                            col += 1
                                            
                                            receipt_date = sl.picking_id.date_done
                                            worksheet.write(row, col, str(receipt_date.strftime('%d/%m/%Y') if receipt_date else 'N/A'), style_normal)
                                            col += 1
                                            
                                            worksheet.write(row, col, str(sl.quantity_done), style_normal)
                                            col += 1
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
