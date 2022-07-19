from odoo import api, fields, models, _


class account_move_inherit(models.Model):
    _inherit = "account.move"


    sale_id = fields.Many2one("sale.order", string="SO No", compute="_get_sale_id", store=True)

    @api.depends('invoice_origin')
    def _get_sale_id(self):
        for record in self:
            if record.invoice_origin:
                if 'SO' in record.invoice_origin:
                    sale = self.env['sale.order'].search([('name', '=', record.invoice_origin)])
                    record.sale_id = sale.id



    