from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    vendor_type_id = fields.Many2one(comodel_name="vendor.type", string="Vendor Type")