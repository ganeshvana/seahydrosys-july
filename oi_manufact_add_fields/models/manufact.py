from odoo import api, fields, models, tools, _


class UserRestriction(models.Model):
    _inherit = "mrp.production"


    note = fields.Many2one('mrp.note', string='Note')


# class purchase_order(models.Model):
#     _inherit = "purchase.order"


#     tax_country_id = fields.Many2one("res.country",'Country')



# class StockPickingStage(models.Model):
#     _inherit = "stock.picking"

#     show_allocation = fields.Boolean('Show Allocation')


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"


class MrpWorkorderProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    employee = fields.Many2one('hr.employee','Employee')


class MrpNote(models.Model):
    _name="mrp.note"
    _description="Note"

    name = fields.Char("")


class StockMove(models.Model):
    _inherit = "stock.move"
    
    product_reference  = fields.Char("Model Number", compute="_compute_product_reference")
    
               
    @api.depends('product_id', 'product_reference')
    def _compute_product_reference(self):
        for rec in self:
            if rec.product_id:
                rec.product_reference = rec.product_id.product_reference
            else:
                rec.product_reference = False

    