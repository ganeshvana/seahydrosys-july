from odoo import models, fields, _
import io
import base64
import xlsxwriter
from datetime import date


class TransactioneDetails(models.TransientModel):
    _name = 'transaction.details'
    _description = 'Fill Rate Summary Report'
    
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()
    transaction_type = fields.Selection([
        ('rtgs', "R-RTGS"),
        ('neft', "N-NEFT"),
        ('fund_tranfer', "I-Funds Transfer"),
        ('imps', "M-IMPS"),
    ], required=True)
    
    
    def transaction_details_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Payment Report')
        style_highlight_right = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'right'})
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'center'})
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
        merge_formatb.set_font_size(15)

        headers = [
            'S/N', 'Transaction Type', 'Beneficiary Code', 'Beneficiary Account Number', 'Transaction Amount', 
            'Beneficiary Name', 'Drawee Location in case of Demand Draft', 'DD Printing Location', 'Beneficiary Address 1',
            'Beneficiary Address 2', 'Beneficiary Address 3', 'Beneficiary Address 4', 'Beneficiary Address 5',
            'Instruction Reference Number', 'Customer Reference Number', 'Payment details 1', 'Payment details 2',
            'Payment details 3', 'Payment details 4', 'Payment details 5', 'Payment details 6', 'Payment details 7',
            'Cheque Number', 'Chq / Trn Date', 'MICR Number', 'IFC Code', 'Beneficiary Bank Name', 'Beneficiary Bank Branch Name', 
            'Beneficiary email id','Format'
        ]

        row = 1
        worksheet.merge_range(f'A{row}:T{row}', 'HDFC ENET UPLOAD', merge_formatb)
        row += 1

        for col, header in enumerate(headers):
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 14)
        
        row += 1
        sn = 1  

        context = self._context
        active_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        partner_data = {}

        if active_model == 'account.move':
            for index, val in enumerate(active_ids, start=1):
                move = self.env['account.move'].browse(val)

                partner = move.partner_id.id

                payments_vals = move._get_reconciled_info_JSON_values()
                payment_amount = move.amount_residual

                if partner in partner_data:
                    partner_data[partner]['amount'] += payment_amount 
                else:
                    partner_data[partner] = {
                        'move': move,
                        'amount': payment_amount,  
                        'payment_date': payments_vals[0].get('date') if payments_vals else None
                    }

            for partner_id, data in partner_data.items():
                move = data['move']

                worksheet.write(row, 0, sn, style_normal)
                sn += 1

                values = [
                    dict(self._fields['transaction_type'].selection).get(self.transaction_type, '').split('-')[0],
                    '', 
                    move.partner_id.bank_ids and move.partner_id.bank_ids[0].acc_number or '',  
                    data['amount'],  
                    move.partner_id.name or '',  
                    '', '', '', '', '', '', '', '',  
                    move.partner_id.ref or '', 
                    '', '', '', '', '', '', '', '',  
                ]

                for col, value in enumerate(values, start=1):
                    worksheet.write(row, col, value, style_normal)

                payment_date_str = date.today().strftime('%d/%m/%Y')
                bank_name = move.partner_id.bank_ids and move.partner_id.bank_ids[0].bank_id.name or ''
                ifsc = move.partner_id.bank_ids and move.partner_id.bank_ids[0].bank_id.bic or ''
                worksheet.write(row, 23, payment_date_str, style_normal)
                worksheet.write(row, 25, ifsc, style_normal)
                worksheet.write(row, 26, bank_name, style_normal)
                worksheet.write(row, 28, move.partner_id.email or '', style_normal)

                combined_values = ','.join([str(v) if v else '' for v in values + [payment_date_str, '', ifsc, bank_name, '', move.partner_id.email]])
                worksheet.write(row, 29, combined_values, style_normal)

                row += 1


        workbook.close()
        xlsx_data = output.getvalue()
        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "hdsfc_enet_upload.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }



