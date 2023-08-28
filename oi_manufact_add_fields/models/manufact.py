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











    