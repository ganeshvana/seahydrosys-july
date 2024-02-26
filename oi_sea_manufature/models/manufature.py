from odoo import api, fields, models, tools, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sea_delivery_date = fields.Date(string="Delivery Date", tracking=True)
    sea_batch_no = fields.Text(string="Batch No", tracking=True)
    origin_name = fields.Char(compute='_compute_origin_name',)
    
    @api.depends('origin')
    def _compute_origin_name(self):
        for mo in self:
            if mo.origin:
                # Split values by comma
                origin_names = mo.origin.split(',')
                filtered_names = [name.strip() for name in origin_names if name[:2] == mo.name[:2]]
                
                if filtered_names:
                    mo.origin_name = ', '.join(filtered_names)
                else:
                    # If mo.origin_name is still empty, try splitting by dash
                    origin_dash = mo.origin.split('-')
                    for origin_name in origin_dash:
                        mo.origin_name = origin_name
            else:
                mo.origin_name = False