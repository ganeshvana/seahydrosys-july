from odoo import models, fields, _
import io
import base64
import xlsxwriter


class TransactioneDetails(models.TransientModel):
    _name = 'transaction.details'
    _description = 'Fill Rate Summary Report'
    
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    transaction_type = fields.Selection([
        ('rtgs', "R-RTGS"),
        ('neft', "N-NEFT"),
        ('fund_tranfer', "I-Funds Transfer"),
        ('imps', "M-IMPS"),
    ], required=True)

    def transaction_details_report(self):
        def setup_workbook():
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Transaction Details Report')

            bold_style = workbook.add_format({'bold': True, 'align': 'center'})
            center_style = workbook.add_format({'align': 'center'})
            title_style = workbook.add_format({
                'bold': True,
                'align': 'center',
                'font_size': 14,
                'bg_color': '#FFD39B',
            })

            title = f"Transaction Details"
            worksheet.merge_range('A1:AC1', title, title_style)

            headers = [
                'S/N', 'Transaction Type', 'Beneficiary Code', 'Beneficiary Account Number', 'Transaction Amount', 'Beneficiary Name',
                'Drawee Location in case of Demand Draft', 'DD Printing Location', 'Beneficiary Address 1',
                'Beneficiary Address 2', 'Beneficiary Address 3', 'Beneficiary Address 4', 'Beneficiary Address 5',
                'Instruction Reference Number', 'Customer Reference Number', 'Payment details 1', 'Payment details 2',
                'Payment details 3', 'Payment details 4', 'Payment details 5', 'Payment details 6', 'Payment details 7',
                'Cheque Number', 'Chq / Trn Date', 'MICR Number', 'IFC Code', 'Beneficiary Bank Name', 
                'Beneficiary Bank Branch Name', 'Beneficiary email id',
            ]

            for col, header in enumerate(headers):
                worksheet.write(1, col, header, bold_style)

            return workbook, worksheet, output, center_style

        def write_transaction_details(move_records, worksheet, center_style):
            row = 2
            for idx, move in enumerate(move_records, start=1):
                worksheet.write(row, 0, idx, center_style)  
                worksheet.write(row, 1, dict(self._fields['transaction_type'].selection).get(self.transaction_type), center_style)  
                worksheet.write(row, 2, move.partner_id.ref or '', center_style)  
                worksheet.write(row, 3, move.partner_id.bank_ids and move.partner_id.bank_ids[0].acc_number or '', center_style)  
                worksheet.write(row, 5, move.partner_id.name or '', center_style)  

                payments_vals = move._get_reconciled_info_JSON_values()
                payment_dates = [payment.get('date') for payment in payments_vals]
                payment_amounts = [payment.get('amount') for payment in payments_vals]

                bank_name = move.partner_id.bank_ids and move.partner_id.bank_ids[0].bank_id.name or ''
                worksheet.write(row, 26, bank_name, center_style) 

                if payment_dates and payment_amounts:
                    worksheet.write(row, 23, payment_dates[0].strftime('%d/%m/%Y') if payment_dates else '', center_style)  
                    worksheet.write(row, 4, payment_amounts[0], center_style)  

                worksheet.write(row, 28, move.partner_id.email or '', center_style)  
                row += 1

        if self.start_date and self.end_date and self.start_date <= self.end_date:
            move_records = self.env['account.move'].search([
                ('invoice_date', '>=', self.start_date),
                ('invoice_date', '<=', self.end_date),
                ('move_type', '=', 'in_invoice'),  
                ('state', '=', 'posted'),
            ])
        else:
            move_records = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'), 
                ('state', '=', 'posted'),
            ])

        workbook, worksheet, output, center_style = setup_workbook()

        write_transaction_details(move_records, worksheet, center_style)

        workbook.close()
        xlsx_data = output.getvalue()
        output.close()

        xls_file = base64.b64encode(xlsx_data)
        self.write({
            'xls_filename': f'Transaction_Details_Report.xlsx',
            'xls_file': xls_file,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=transaction.details&id={self.id}&field=xls_file&download=true&filename={self.xls_filename}',
            'target': 'new',
        }

