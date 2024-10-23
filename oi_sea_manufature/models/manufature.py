from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sea_delivery_date = fields.Date(string="Delivery Date", tracking=True)
    sea_batch_no = fields.Text(string="Batch No", tracking=True)
    
    def button_mark_done(self):
        for production in self:
            pickings = production.picking_ids.filtered(lambda p: p.state != 'done')
            if pickings:
                # raise ValidationError("You cannot validate the Manufacturing Order until all related stock transfers are in 'Done' state.")
                production.write({'state': 'done'})
            return super(MrpProduction, self).button_mark_done()