# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import re

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path
from odoo.tools.misc import xlsxwriter


class BOMStructureXl(models.TransientModel):
    _name = 'bom.structure.xl'
    _inherit = 'report.mrp.report_bom_structure'
    _description = 'BOM Structure Xl'
    
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()


    # def action_generate_xls(self):
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet('BoM Details')
    #     left = workbook.add_format({'align': 'left', 'bold': True})
    #     left1 = workbook.add_format({'align': 'left'})
    #     bold = workbook.add_format({'bold': True,'align': 'left'})
    #     bold_right = workbook.add_format({'bold': True,'align': 'right'})
    #     style_highlight_right = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'right'})
    #     style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
    #     style_normal = workbook.add_format({'align': 'center'})
    #     style_right = workbook.add_format({'align': 'right'})
    #     style_left = workbook.add_format({'align': 'left'})
    #     date_format = workbook.add_format({'num_format': 'dd/mm/yy hh:mm:ss', 'align':'left'})
    #     dt_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align':'left'})
    #     dt_format1 = workbook.add_format({'num_format': 'dd/mm/yy', 'align':'center'})
    #     middle = workbook.add_format({'bold': True, 'align':'center', 'fg_color': '#AAA4A3'})
    #     merge_formatb = workbook.add_format({
    #             'bold': 1,
    #             'border': 1,
    #             'align': 'center',
    #             'valign': 'vcenter',
    #             'bg_color': '#FFFFFF',
    #             'text_wrap': True
    #             })
    #     heading_format = workbook.add_format({'align':'center',
    #                                         'valign':'vcenter',
    #                                         'bold':True,
    #                                         'size':14,
    #                                         'fg_color': '#AAA4A3'
    #                                         })
    #     light_blue =workbook.add_format({'fg_color':'#3DE0E3','align': 'left'})
    #     blue =workbook.add_format({'fg_color':'#208EB0','align': 'left'})
    #     light_blue_right =workbook.add_format({'fg_color':'#3DE0E3','align': 'right'})
    #     blue_right =workbook.add_format({'fg_color':'#208EB0','align': 'right'})
    #     merge_formatb.set_font_size(9)
    #     worksheet.set_column('B4:B4', 18)
    #     worksheet.set_column('C4:C4', 18)
    #     worksheet.set_column('D4:D4', 15)
    #     worksheet.set_column('E4:E4', 15)
    #     worksheet.set_column('F4:G4', 10)
    #     worksheet.set_column('H4:H4', 10)
    #     c = 0
    #     # context = self._context
    #     context = 
    #     active_ids = context['active_ids']
    #     print ("active_ids",active_ids)  
    #     for val in active_ids:
    #         bill = self.env['mrp.bom'].browse(val)
    #         pro = self.env['']
    #     worksheet.write(2, 1, 'Product', left)
    #     worksheet.write(2, 2, pro.product_tmpl_id, left1)



    #     workbook.close()
    #     xlsx_data = output.getvalue()

    #     self.xls_file = base64.encodebytes(xlsx_data)
    #     self.xls_filename = "BoM_Structure.xlsx"

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': self._name,
    #         'view_mode': 'form',
    #         'res_id': self.id,
    #         'views': [(False, 'form')],
    #         'target': 'new',
    #     }


    def action_generate_xls(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('BoM Details')
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'right'})
        style_footer = workbook.add_format({'bold': True, 'align': 'right'})
        row = 0
        col = 0
        active_ids = self._context['active_ids']            
        if active_ids:
            for rec in active_ids:                
                bom = self.env['mrp.bom'].browse(rec)
                data = {'context': {'tz': 'Asia/Kolkata', 'uid': 2, 'allowed_company_ids': [1]}, 'report_type': 'pdf'}
                vals = self._get_report_values([bom.id], data=data)
                cost = 0.0
                rows = []
                foot = []
                headers =[
                    "Product",
                    "Product Name",
                    "Intenal Reference",
                    # "Product Category",
                    "Quantity",
                    "Unit of Measure",
                    "Product Cost",
                    "BoM Cost",

                ] 
                 # "BoM Version",
                    # "ECO(s)",
                for pro in vals['docs']:
                    # price = str("%.2f" % round(pro['price'], 2))
                    # total = pro['total'] / pro['quantity']
                    currency = pro['currency']
                    split_ref = pro['code'].split(']')
                    ref = split_ref[0].replace('[','')
                    # product_name = split_ref[1]
                    rows.append((
                        pro['code'],
                        pro['code'],
                        ref,
                        # pro['product_id'].categ_id.name,
                        # pro['version'],
                        # pro['ecos'],
                        str(pro['bom'].product_qty)+'0',
                        pro['bom'].product_uom_id.name,
                        # currency.symbol + str("%.2f" % round(pro['price'], 2)),
                        # currency.symbol + str("%.2f" % round(pro['total'], 2)),
                        ))
                    print("88888888888888888888888888888888888",row)
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

                        rows.append((
                        line['name'],
                        line['name'],
                        # product_name,
                        ref,
                        # ref,
                        # line['version'],
                        # line['ecos'],
                        str(line['quantity']) + '0',
                        line['uom'],
                        currency.symbol + str("%.2f" % round(line['prod_cost'], 2)),
                        currency.symbol + str("%.2f" % round(line['bom_cost'], 2)),
                    ))
                        print("MMMMMMMMMMMMMMMMMSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",rows)
                foot.append((
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        ))
                col = 0
                worksheet.write(row, col, bom.product_tmpl_id.name, style_highlight)
                for header in headers:
                    worksheet.write(row, col, header, style_highlight)
                    worksheet.set_column(col, col, 30)
                    col += 1
        
                row = 1
                col += 1

                for lined in rows:

                    col = 0
                    for d in lined:
                        worksheet.write(row, col, d, style_normal)
                        col += 1
                    row += 1
                for linef in foot:
                    col = 0
                    for f in linef:
                        worksheet.write(row, col, f, style_footer)
                        col += 1
                    row += 1

        workbook.close()
        xlsx_data = output.getvalue()

        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "BoM_Structure.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    


    
