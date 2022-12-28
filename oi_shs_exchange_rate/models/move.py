from odoo import api, fields, models, _
from datetime import datetime



class account_move(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float('Customs FX Rate')
    fx_currency_id = fields.Many2one('res.currency','FX Currency',compute='_get_currency')
    total_fx_amount = fields.Float('Total Fx',compute='_get_total')

   

    @api.depends('invoice_line_ids.total_exchange_amount')
    def _get_total(self):
        for record in self:
            total_fx = 0
            for line in record.invoice_line_ids:
                total_fx += line.total_exchange_amount
            record.total_fx_amount = total_fx
            


    @api.depends('exchange_rate')
    def _get_currency(self):
        for record in self:
            record.fx_currency_id = ''
            if record.exchange_rate != 0:
                cur_obj = self.env['res.currency'].search([('name','=','INR')])
                if cur_obj:
                    record.fx_currency_id = cur_obj.id
                else:
                    record.fx_currency_id = ''


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    exchange_amount = fields.Float('FX Amount',compute='_get_exchange_amount')
    total_exchange_amount = fields.Float('Total FX Amount',compute='_get_exchange_amount')


#     @api.multi
    @api.depends('move_id')
    def _get_exchange_amount(self):
        exchange_amount = 0
        tot_exchange_amount = 0
        for record in self:
            if record.move_id and record.move_id.exchange_rate != 0:
                exchange_amount = record.price_unit * record.move_id.exchange_rate
                tot_exchange_amount = record.price_subtotal * record.move_id.exchange_rate
            record.exchange_amount = exchange_amount
            record.total_exchange_amount = tot_exchange_amount
            
            

    
