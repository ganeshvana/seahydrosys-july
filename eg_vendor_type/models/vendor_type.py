from odoo import models, fields


class VendorType(models.Model):
    _name = "vendor.type"
    _description = "Vendor Type"

    name = fields.Char(string="Name")
