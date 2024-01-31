from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import timedelta

class picking(models.Model):
    _inherit = "stock.picking"
    
    todo_date = fields.Date("To Do Date")
    
    def button_validate(self):
        result = super(picking, self).button_validate()
        internal = self.env['stock.picking'].search([('origin', '=', self.origin), ('picking_type_code', '=', 'internal')])
        if internal:        
            internal.todo_date = fields.Date.today()  +  timedelta(days=3)
        return result

class purchase_order(models.Model):
    _inherit = "purchase.order"
 
    # mo_product = fields.Char("MO Product",compute="_get_mo_product")   
    despatch_through = fields.Char(string="Despatch Through",tracking=True)
    due_date = fields.Date("Due Date",tracking=True)
    sail_date = fields.Date("Sail Date",tracking=True)
    tax_country_id = fields.Many2one("res.country",'Country',tracking=True)
    # pick_id = fields.Many2one('stock.picking','DO')
    total_weight = fields.Float(
        compute="_compute_total_physical_properties",
        digits="Stock Weight",
    )
    total_volume = fields.Float(
        compute="_compute_total_physical_properties", digits="Volume"
    )
    weight_uom_name = fields.Char(compute="_compute_total_physical_properties")
    volume_uom_name = fields.Char(compute="_compute_total_physical_properties")
    display_total_weight_in_report = fields.Boolean(
        "Display Weight in Report", default=True
    )
    display_total_volume_in_report = fields.Boolean(
        "Display Volume in Report", default=True
    )

    @api.depends("order_line.product_uom_qty", "order_line.product_id")
    def _compute_total_physical_properties(self):
        for po in self:
            po.total_weight = 0
            po.total_volume = 0
            po.weight_uom_name = ""
            po.volume_uom_name = ""

            if po.company_id.display_order_weight_in_po:
                weight_uoms = po.mapped("order_line.product_id.weight_uom_name")
                # values are computed only if all products in PO have same UOMs.
                if len(weight_uoms) > 0:
                    same_weight_uom = all(el == weight_uoms[0] for el in weight_uoms)
                    if same_weight_uom:
                        po.total_weight = sum(po.mapped("order_line.line_weight"))
                        po.weight_uom_name = weight_uoms[0]

            if po.company_id.display_order_volume_in_po:
                volume_uoms = po.mapped("order_line.product_id.volume_uom_name")
                if len(volume_uoms) > 0:
                    same_volume_uom = all(el == volume_uoms[0] for el in volume_uoms)
                    if same_volume_uom:
                        po.total_volume = sum(po.mapped("order_line.line_volume"))
                        po.volume_uom_name = volume_uoms[0]

    

    # @api.depends('origin')
    # def _get_mo_product(self):
    #     self.mo_product = ''
    #     for order in self:
    #         if self.origin:
    #             mo = self.env['mrp.production'].search([('name', '=', self.origin)])
    #             if mo:
    #             	self.mo_product = mo.product_id.name
    #             else:
    #                 self.mo_product = ''

    # def action_mo(self):
    #     for order in self:
    #         for line in order.order_line:
    #             if order.mo_product:
    #                 line.write({'name':order.mo_product})









class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"
 
   
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Purchase Price'),tracking=True)
    line_weight = fields.Float(
        "Weight", compute="_compute_line_physical_properties", digits="Stock Weight"
    )
    line_volume = fields.Float(
        "Volume", compute="_compute_line_physical_properties", digits="Volume"
    )

    @api.depends("product_uom_qty", "product_id")
    def _compute_line_physical_properties(self):
        for line in self:
            line.line_weight = line.product_id.weight * line.product_uom_qty
            line.line_volume = line.product_id.volume * line.product_uom_qty


class accoount_invoice_line(models.Model):
    _inherit = "account.move.line"
 
   
    price_unit = fields.Float(string='Price', digits=dp.get_precision('Purchase Price'),tracking=True)


   
