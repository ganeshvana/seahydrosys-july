from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    vendor_type_id = fields.Many2one(comodel_name="vendor.type", string="Vendor Type", related="name.vendor_type_id")