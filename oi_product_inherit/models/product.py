from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time
import re






class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_reference  = fields.Char("Model Number")
        
    @api.model
    def create(self, vals):
        categ_id = vals.get('categ_id')
        if categ_id:
            category = self.env['product.category'].browse(categ_id)
            if category and category.if_product_seq:
                prefix = category.product_code
                vals['product_reference'] = self._generate_sequence(prefix)
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        categ_id = vals.get('categ_id')
        if categ_id:
            category = self.env['product.category'].browse(categ_id)
            if category and category.if_product_seq:
                prefix_new = category.product_code 
                for product in self:
                    current_category = product.categ_id
                    prefix_current = current_category.product_code
                    if prefix_new != prefix_current:
                        vals['product_reference'] = self._generate_sequence(prefix_new)
        return super(ProductTemplate, self).write(vals)

    def _generate_sequence(self, prefix):
        if not prefix:
            return False
        prefix = prefix.upper().strip()
        domain = [('product_reference', '=ilike', f'{prefix}%')]
        last_product = self.env['product.template'].search(domain, order="product_reference desc", limit=1)
        next_sequence_number = 1
        if last_product and last_product.product_reference:
            pattern = rf'^{re.escape(prefix)}(\d+)$'
            match = re.match(pattern, last_product.product_reference)
            if match:
                last_sequence_number = int(match.group(1))
                next_sequence_number = last_sequence_number + 1
            else:
                next_sequence_number = 1
        next_reference = f"{prefix}{str(next_sequence_number).zfill(5)}"
        return next_reference

    @api.constrains('purchase_ok', 'seller_ids')
    def _check_seller_ids(self):
        for product in self:
            if product.purchase_ok and not product.seller_ids:
                raise ValidationError("If Purchase OK is set to True, Add a vendor details")


    @api.constrains('standard_price')
    def _check_standard_price(self):
        for record in self:
            if record.standard_price <= 0.00:
                raise ValidationError('The value of Cost must be greater than 0.00.')

    @api.constrains('sale_delay')
    def _check_sale_delay(self):
        for record in self:
            if record.sale_delay <= 0.00:
                raise ValidationError('The value of Customer Lead Time  must be greater than 0.00.')

    # @api.constrains('produce_delay')
    # def _check_produce_delay(self):
    #     for record in self:
    #         if record.produce_delay <= 0.00:
    #             raise ValidationError('The value of Manuf. Lead Time  must be greater than 0.00.')


    @api.constrains('sale_ok', 'sale_delay')
    def _check_sale_delay(self):
        for product in self:
            if product.sale_ok and not product.sale_delay:
                raise ValidationError("If sale OK is set to True, Add a Customer Lead Time")


    # @api.constrains('route_ids', 'produce_delay')
    # def _check_produce_delay(self):
    #     for product in self:
    #         if product.route_ids and not product.produce_delay:
    #             raise ValidationError("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


    shs_bore = fields.Char(string="Bore",store=True)
    shs_stroke = fields.Char(string="Stroke",store=True)
    shs_rod = fields.Char(string="Rod",store=True)
    shs_class = fields.Char(string="Class",store=True)
    shs_heavy_light = fields.Char(string="Heavy / Light",store=True)
