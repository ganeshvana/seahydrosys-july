# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import re

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import api, fields, models, _
from odoo.tools.misc import xlsxwriter


class BOMStructureXl(models.TransientModel):
    _name = 'bom.structure.xl'
    _inherit = 'report.mrp.report_bom_structure'
    _description = 'BOM Structure Xl'
    
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()

    def action_generate_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'bom.structure.xl'
        datas['form'] = self.read()[0]
        if 'ids' in datas:
            bom_ids = self.env['mrp.bom'].search([('id','in',datas['ids'])])
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Report')
        style_highlight_right = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'right'})
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'center'})
        style_right = workbook.add_format({'align': 'right'})
        style_left = workbook.add_format({'align': 'left'})
        count = 0
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
            "S.No.",
            "Product Name",
            "Intenal Reference",
            "Product Category",
            "Quantity",
            "Unit of Measure",
            "Product Cost",
            "BoM Cost",
        ]
        row = 1
        col = 0

        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 10)
            col += 1       
        row += 1

        for rec in bom_ids:
            count += 1
            col = 0 
            is_main_component = True  # Flag to identify the main component
            worksheet.write(row, col, str(count), style_right)
            col += 1   
            data = {'context': {'tz': 'Asia/Kolkata', 'uid': 2, 'allowed_company_ids': [1]}, 'report_type': 'pdf'}
            vals = self._get_report_values([rec.id], data=data)
            cost = 0.0
            rows = []

            for rec in vals['docs']:
                parent_bom_cost = rec['product'].standard_price
                product_cost += rec['prod_cost'] if 'prod_cost' in rec else 0.0
                currency = rec['currency']
                split_ref = rec['code'].split(']')
                ref = split_ref[0].replace('[','')
                # product_name = split_ref[1]
                rows.append((
                    count if is_main_component else '',  # Add sequence number only for the main component
                    # product_name,
                    rec['code'],
                    ref,
                    rec['product'].categ_id.complete_name,
                    str(rec['bom'].product_qty)+'0',
                    # str(rec['product_qty'])+'0',
                    rec['bom'].product_uom_id.name,
                    currency.symbol + str("%.2f" % round(parent_bom_cost, 2)),
                    # currency.symbol + str("%.2f" % round(product_cost,2))
                ))
                is_main_component = False  # Update flag after processing the main component

            for a in vals['docs']:
                for line in a['lines']:
                    if not 'prod_cost' in line:
                        line['prod_cost'] = 0.0
                    if not 'bom_cost' in line:
                        line['bom_cost'] = 0.0
                    product_ref = line['name'].split(']')
                    ref = product_ref[0].replace('[','')
                    # if len(product_ref) >1:
                    #     product_name = product_ref[1]
                    # else:
                    #     product_name = ''
                    if ref:
                        product = self.env['product.product'].search([('default_code', '=', ref)])
                        if product:
                            categ = product.categ_id[0].complete_name
                        else:
                            categ = ''
                    rows.append((
                        '',
                        # product_name,
                        line['name'],
                        ref,
                        categ,
                        str(line['quantity']) + '0',
                        line['uom'],
                        currency.symbol + str("%.2f" % round(line['prod_cost'], 2)),
                        currency.symbol + str("%.2f" % round(line['bom_cost'], 2)),
                    ))

            col = 0

            for lined in rows:
                col = 0
                for d in lined:
                    worksheet.write(row, col, d, style_normal)
                    col += 1
                row += 1

        row += 1
        workbook.close()
        xlsx_data = output.getvalue()
        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "BOM Report.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

#********************************MO BOM**************************
    
class MRPBOMStructureXl(models.TransientModel):
    _name = 'mrp.bom.structure.xl'
    _inherit = 'report.mrp.report_bom_structure'
    _description = 'BOM Structure Xl'
    
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()
 
    
    def action_generate_product_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'mrp.bom.structure.xl'
        datas['form'] = self.read()[0]
        if 'ids' in datas:
                mrp_ids = self.env['mrp.production'].search([('id','in',datas['ids'])])
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Report')
        style_highlight_right = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'right'})
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'center'})
        style_right = workbook.add_format({'align': 'right'})
        style_left = workbook.add_format({'align': 'left'})
        count = 0
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
                                "S.No",
                                "Product Name",
                                "Internal Reference",
                                "Product Category",
                                "Quantity",
                                "Unit of Measure",
                                # "Product Cost",
                                # "BoM Cost",
                                "MO Number",
                                "Delivery Date",
                                "Batch Number",
                                "MO Qty",
                                "On-hand Qty"

        ]
        row = 1
        col = 0
 
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 10)
            col += 1       
        row += 1
           
        for record in mrp_ids:
            
            is_main_component = True  # Flag to identify the main component
            
            name = record.name
            bom_name = record.bom_id.product_tmpl_id.name
            if record.sea_delivery_date:
                delivery_date = str(record.sea_delivery_date.strftime('%d/%m/%Y'))
            else:
                delivery_date = ''
            if record.sea_batch_no: 
                batch_no = record.sea_batch_no
            else:
                batch_no = ''
            product_qty = record.product_qty
            
            count += 1
            col = 0 

            for product in record.bom_id:
                
                col = 0
                worksheet.write(row, col, str(count),style_right)
                col += 1   
                data = {'context': {'tz': 'Asia/Kolkata', 'uid': 2, 'allowed_company_ids': [1]}, 'report_type': 'pdf'}
                vals = self._get_report_values([product.id], data=data)
                
                cost = 0.0
                rows = []
               
                for rec in vals['docs']:
                    
                    currency = rec['currency']
                    split_ref = rec['code'].split(']')
                    ref = split_ref[0].replace('[','')
                    # product_name = split_ref[1]
                    if ref:
                        product_on_hand = self.env['product.template'].search([('name', '=', record.bom_id.product_tmpl_id.name)])
                        if product_on_hand:
                            for record in product_on_hand:
                                on_hand = record.qty_available
                        else:
                            on_hand = ''
                    rows.append((
                        count if is_main_component else '',  # Add sequence number only for the main component
                        bom_name,
                        ref,
                        rec['product'].categ_id.complete_name,
                        str(rec['bom'].product_qty)+'0',
                        rec['bom'].product_uom_id.name,
                        # '',
                        # '',
                        name,
                        delivery_date,
                        batch_no,
                        product_qty,
                        on_hand
                        
                        
                        ))
                    is_main_component = False  # Update flag after processing the main component

                for a in vals['docs']:
                    for line in a['lines']:
                        if line['type'] == 'bom' or line['type'] == 'component':
                           
                            if line['type'] != 'subcontract':
                                if not 'prod_cost' in line:
                                    line['prod_cost'] = 0.0
                                if not 'bom_cost' in line:
                                    line['bom_cost'] = 0.0
                                product_ref = line['name'].split(']')
                                ref = product_ref[0].replace('[','')
                                # if len(product_ref) >1:
                                #     product_name = product_ref[1]
                                # else:
                                #     product_name = ''
                                if ref:
                                    product = self.env['product.product'].search([('default_code', '=', ref)])
                                    product_on_hand = self.env['product.template'].search([('default_code', '=', ref)])
                                    if product_on_hand:
                                        for record in product_on_hand:
                                            on_hand = record.qty_available
                                    else:
                                        on_hand = ''
                                    
                                    if product:
                                        for categ in product:
                                            category_id = categ.categ_id
                                            categ = category_id.complete_name
                                    else:
                                        categ = ''
                                    if categ:
                                
                                        rows.append((
                                            '',
                                        line['name'],
                                        ref,
                                        categ,
                                    
                                        str(line['quantity']) + '0',
                                        line['uom'],
                                    
                                        '','','',
                                        line['quantity']* product_qty, 
                                        on_hand                       

                                    
                                    ))
                col = 0
 

                for lined in rows:

                    col = 0
                    for d in lined:
                        worksheet.write(row, col, d, style_normal)
                        col += 1
                    row += 1
                

            
        row += 1
        workbook.close()
        xlsx_data = output.getvalue()
        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "Report.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }   










    
