from odoo import api, fields, models, tools, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sea_delivery_date = fields.Date(string="Delivery Date")
    sea_batch_no = fields.Text(string="Batch No")