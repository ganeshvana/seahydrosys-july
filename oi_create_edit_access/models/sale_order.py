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

    # @api.model
    # def create(self, vals):
    #     res = super(SaleOrderLine, self).create(vals)
    #     self._create_notification_log(res, 'created')
    #     return res

    # def write(self, vals):
    #     res = super(SaleOrderLine, self).write(vals)
    #     if vals.get('product_id') or vals.get('name') or vals.get('product_uom_qty'):
    #         self._create_notification_log(self, 'edited')
    #     return res

    # def unlink(self):
    #     deleted_lines = self.filtered(lambda line: line.exists())
    #     res = super(SaleOrderLine, deleted_lines).unlink()
    #     for line in deleted_lines:
    #         self._delete_notification_log(line, 'deleted')
    #     return res
    
    # def _delete_notification_log(self, line, action):
    #     subtype = self.env['mail.message.subtype'].search([('name', '=', 'Note')], limit=1)
    #     if action == 'deleted':
    #         body = '<p>Sale Order Line deleted:</p>'

    #     edit_message = self.env['mail.message'].create({
    #         'subject': f'{action.capitalize()} in Sale Order Line',
    #         'body': body,
    #         'message_type': 'notification',
    #         'model': 'sale.order',
    #         'res_id': line.order_id.id,
    #         'subtype_id': subtype.id
    #     })

    # def _create_notification_log(self, line, action):
    #     subtype = self.env['mail.message.subtype'].search([('name', '=', 'Note')], limit=1)
    #     if action == 'created':
    #         body = '<p>Sale Order Line created:</p>'
    #     elif action == 'edited':
    #         body = '<p>Sale Order Line edited:</p>'
    #     # elif action == 'deleted':
    #     #     body = '<p>Sale Order Line deleted:</p>'
    #     body += f'<p>Product: {line.product_id.name}</p>' if line.product_id else ''
    #     body += f'<p>Description: {line.name}</p>' if line.name else ''
    #     body += f'<p>Quantity: {line.product_uom_qty}</p>' if line.product_uom_qty else ''

    #     edit_message = self.env['mail.message'].create({
    #         'subject': f'{action.capitalize()} in Sale Order Line',
    #         'body': body,
    #         'message_type': 'notification',
    #         'model': 'sale.order',
    #         'res_id': line.order_id.id,
    #         'subtype_id': subtype.id
    #     })
    
    
    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)

        subtype = self.env['mail.message.subtype'].search(
            [('name', '=', 'Note')], limit=1)

        body_dynamic_html = '<p>Sale Order Line created:</p>'
        if res.product_id:
            body_dynamic_html += '<p>Product: %s</p>' % (res.product_id.name)
        if res.name:
            body_dynamic_html += '<p>Description: %s</p>' % (res.name)
        if res.product_uom_qty:
            body_dynamic_html += '<p>Quantity: %s</p>' % (res.product_uom_qty)

        edit_message = self.env['mail.message'].create({
            'subject': 'Sale Order Line',
            'body': body_dynamic_html,
            'message_type': 'notification',
            'model': 'sale.order',
            'res_id': res.order_id.id,
            'subtype_id': subtype.id
        })

        return res

    # def write(self, vals):
    #     res = super(SaleOrderLine, self).write(vals)

    #     if 'product_id' in vals:
    #         subtype = self.env['mail.message.subtype'].search(
    #             [('name', '=', 'Note')], limit=1)
    #         body_dynamic_html = '<p>%s was edited product </p> </div>' % (self.product_id.name)
                    
    #         edit_message = self.env['mail.message'].create({
    #             'subject': 'Edited in Sale Order Line',
    #             'body': body_dynamic_html,
    #             'message_type': 'notification',
    #             'model': 'sale.order',
    #             'res_id': self.order_id.id,
    #             'subtype_id': subtype.id
    #         })

    #     if 'name' in vals:
    #         subtype = self.env['mail.message.subtype'].search(
    #             [('name', '=', 'Note')], limit=1)
    #         body_dynamic_html = '<p>%s was edited in description </p> </div>' % (self.name)
    #         edit_message = self.env['mail.message'].create({
    #             'subject': 'Edited in Sale Order Line',
    #             'body': body_dynamic_html,
    #             'message_type': 'notification',
    #             'model': 'sale.order',
    #             'res_id': self.order_id.id,
    #             'subtype_id': subtype.id
    #         })

    #     if 'product_uom_qty' in vals:
    #         subtype = self.env['mail.message.subtype'].search(
    #             [('name', '=', 'Note')], limit=1)
    #         body_dynamic_html = '<p>%s was edited in Quantity </p> </div>' % (self.product_uom_qty)
    #         edit_message = self.env['mail.message'].create({
    #             'subject': 'Edited in Sale Order Line',
    #             'body': body_dynamic_html,
    #             'message_type': 'notification',
    #             'model': 'sale.order',
    #             'res_id': self.order_id.id,
    #             'subtype_id': subtype.id
    #         })

    #     return res

 