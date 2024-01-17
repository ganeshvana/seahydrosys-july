from odoo import api, fields, models, tools, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    #Tracking True for all fields in PO