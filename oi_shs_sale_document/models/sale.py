from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_delivery_date = fields.Date("Shipping Date")
    quatation_order_date = fields.Date(string="Order Date")
    # shipping_date = fields.Date(string="Shipping Date")



