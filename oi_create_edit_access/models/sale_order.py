from odoo import api, fields, models, tools, _

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

from odoo.addons.payment import utils as payment_utils


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)

        if 'product_id' in vals:
            subtype = self.env['mail.message.subtype'].search(
                [('name', '=', 'Note')], limit=1)
            body_dynamic_html = '<p>%s was edited product </p> </div>' % (self.product_id.name)
                    
            edit_message = self.env['mail.message'].create({
                'subject': 'Edited in Sale Order Line',
                'body': body_dynamic_html,
                'message_type': 'notification',
                'model': 'sale.order',
                'res_id': self.order_id.id,
                'subtype_id': subtype.id
            })

        if 'name' in vals:
            subtype = self.env['mail.message.subtype'].search(
                [('name', '=', 'Note')], limit=1)
            body_dynamic_html = '<p>%s was edited in description </p> </div>' % (self.name)
            edit_message = self.env['mail.message'].create({
                'subject': 'Edited in Sale Order Line',
                'body': body_dynamic_html,
                'message_type': 'notification',
                'model': 'sale.order',
                'res_id': self.order_id.id,
                'subtype_id': subtype.id
            })

        if 'product_uom_qty' in vals:
            subtype = self.env['mail.message.subtype'].search(
                [('name', '=', 'Note')], limit=1)
            body_dynamic_html = '<p>%s was edited in Quantity </p> </div>' % (self.product_uom_qty)
            edit_message = self.env['mail.message'].create({
                'subject': 'Edited in Sale Order Line',
                'body': body_dynamic_html,
                'message_type': 'notification',
                'model': 'sale.order',
                'res_id': self.order_id.id,
                'subtype_id': subtype.id
            })

        return res

 