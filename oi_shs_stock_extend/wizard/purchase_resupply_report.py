from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from datetime import datetime,timedelta,timezone
from dateutil.relativedelta import relativedelta
import base64
import io
import os
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo.modules.module import get_resource_path
from odoo.tools.misc import xlsxwriter
from odoo.tools.mimetypes import guess_mimetype
import os.path
from os import path
from pathlib import Path
import collections, functools, operator
from collections import Counter
from reportlab.rl_settings import rtlSupport
from datetime import  date
# from datetimerange import DateTimeRange
from datetime import timedelta
import sys
import pytz


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
        style_highlight_right = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'right'})
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'left'})
        style_right = workbook.add_format({'align': 'right'})
        style_left = workbook.add_format({'align': 'left'})
        merge_formatb = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#FFFFFF',
                'text_wrap': True
                })
        merge_formatb.set_font_size(9)
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
            # "Supply Date",
            "Supply Status",
            "Supply Product",
            "Supply Qty",
            
        ]
        vehicle_list = []
        row = 1
        col = 0
        res_done = receipt_done = 0.0
        total_fuel = total_cost = 0.0
        col = 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 16)
            col += 1       
        row += 1
        purchases = self.env['purchase.order'].search([('state', 'in', ['purchase','done'] )])
        for po in purchases:
            col = 0
            if self.from_date <= po.date_approve.date() <= self.to_date :
                moves_subcontracted = po.order_line.move_ids.filtered(lambda m: m.is_subcontract)
                subcontracted_productions = moves_subcontracted.move_orig_ids.production_id
                subcontracts = subcontracted_productions.picking_ids
                pickings = po.order_line.move_ids
                if subcontracts:
                    worksheet.write(row, col, str(po.name),style_normal)
                    col += 1
                    worksheet.write(row, col, str(po.partner_id.name),style_normal)
                    col += 1
                    worksheet.write(row, col, str(po.date_order.strftime('%d/%m/%Y')),style_normal)
                    col += 1
                    for pol in po.order_line: 
                        col = 3
                        worksheet.write(row, col, str(pol.product_id.name),style_normal)
                        col += 1
                        worksheet.write(row, col, str(pol.product_qty),style_normal)
                        # col += 1
                        # worksheet.write(row, col, str(pol.date_done),style_normal)
                        col += 1                       
                        pick = pickings.filtered(lambda m: m.product_id == pol.product_id)   
                    for val in pick:               
                        col = 5
                        worksheet.write(row, col, str(val.picking_id.name),style_normal)
                        col += 1

                    # Write the 'Receipt Date'
                        worksheet.write(row, col, str(val.picking_id.date_done or ''), style_normal)  # "Receipt Date"
                        # pickings = po.order_line.move_ids
                        # for  in pol.move_ids:
                        #     if movmovee.picking_id:  
                        #         col = 6
                        #         worksheet.write(row, col, str(val.picking_id.date_done or ''), style_normal)
                        col += 1

                        if val.picking_id.state == 'draft':
                            state = 'Draft'
                        if val.picking_id.state == 'waiting':
                            state = 'Waiting for another Operation'
                        if val.picking_id.state == 'confirmed':
                            state = 'Waiting'
                        if val.picking_id.state == 'assigned':
                            state = 'Ready'
                        if val.picking_id.state == 'done':
                            state = 'Done'
                        if val.picking_id.state == 'cancel':
                            state = 'Cancel'
                            
                            worksheet.write(row, col, str(state),style_normal)
                            col += 1
                            pick_sum = sum(p.quantity_done for p in pick)
                            worksheet.write(row, col, str(val.quantity_done),style_normal)
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
                                            col = 9
                                            worksheet.write(row, col, str(sl.picking_id.name),style_normal)
                                            col += 1
                                            if sl.picking_id.state == 'draft':
                                                state = 'Draft'
                                            if sl.picking_id.state == 'waiting':
                                                state = 'Waiting for another Operation'
                                            if sl.picking_id.state == 'confirmed':
                                                state = 'Waiting'
                                            if sl.picking_id.state == 'assigned':
                                                state = 'Ready'
                                            if sl.picking_id.state == 'done':
                                                state = 'Done'
                                            if sl.picking_id.state == 'cancel':
                                                state = 'Cancel'
                                            worksheet.write(row, col, str(state),style_normal)
                                            col += 1
                                            worksheet.write(row, col, str(sl.product_id.name),style_normal)
                                            col += 1
                                            res_done = sl.quantity_done
                                            worksheet.write(row, col, str(sl.quantity_done),style_normal)
                                            col += 1
                                            row+= 1
                    # col = 11
                    # worksheet.write(row, col, receipt_done - res_done,style_normal)
                    # col += 1
                    
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