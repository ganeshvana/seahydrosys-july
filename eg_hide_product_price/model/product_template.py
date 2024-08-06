from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hide_product_cost_price = fields.Boolean(string="Hide Cost Price", compute="_compute_for_hide_product_cost_price")
    hide_product_sale_price = fields.Boolean(string="Hide Sale Price", compute="_compute_for_hide_product_sale_price")

    def _compute_for_hide_product_cost_price(self):
        for rec in self:
            if self.env.user.has_group("eg_hide_product_price.show_cost_price_group"):
                rec.hide_product_cost_price = False
            else:
                rec.hide_product_cost_price = True

    def _compute_for_hide_product_sale_price(self):
        for rec in self:
            if self.env.user.has_group("eg_hide_product_price.show_sale_price_group"):
                rec.hide_product_sale_price = False
            else:
                rec.hide_product_sale_price = True
