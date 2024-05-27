from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_delivery_date = fields.Date("Shipping Date")
<<<<<<< HEAD
    quatation_order_date = fields.Date(string="Order Date")
    # shipping_date = fields.Date(string="Shipping Date")
=======
>>>>>>> 10b7c9b828f7e3e9571c03f290ffe922a9de1cd6



