from odoo import api, fields, models, _
from datetime import datetime

class account_invoice(models.Model):
    _inherit = 'account.move'


    @api.depends('picking_ids')
    def _get_del(self):
        picking = []
        pick_date = []
        for record in self:
            record.delivery_ref = ''
            record.delivery_date = ''
            if record.picking_ids:
                for each in record.picking_ids:
                    pick_search = self.env['stock.picking'].search([('name','=', each.name)])
                    picking.append(pick_search.name)
                    str_date = str(pick_search.date_done)
                    pick_date.append(str_date)
                picking = ', '.join(picking)
                pick_date = ', '.join(pick_date)
                record.delivery_ref = picking 
                record.delivery_date = pick_date


    despatched_through = fields.Char('Despatched Through')
    destination = fields.Char('Country of Final Destination')
    delivery_terms = fields.Text('Terms 0f Delivery')
    notify_party = fields.Text('Notify Party')
    delivery_ref = fields.Char('Despatch Document No',compute=_get_del)
    delivery_date = fields.Char('Delivery Date',compute=_get_del)
    country_of_origin = fields.Char('Country of Origin of Goods')
    description_goods = fields.Char('Description of Goods')
    # country_of_destination = fields.Char('Country of Final Destination')
    port_of_loading = fields.Char('Port of Loading')
    port_of_discharge = fields.Char('Port of Discharge')

    place_of_delivery = fields.Char('Place of Delivery')
    vessel_no = fields.Char('Vessel/Flight No.')
    hs_code = fields.Char('HS Code')



class account_move_line(models.Model):
    _inherit = 'account.move.line'

    part_no = fields.Char('Part No',related='product_id.default_code')
    po_no = fields.Char('PO No')

    
