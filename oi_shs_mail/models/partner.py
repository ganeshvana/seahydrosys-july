from odoo import models, fields, api, _
from datetime import datetime,timedelta


    
class Partner(models.Model):
    _inherit = 'res.partner'
    

    @api.model_create_multi
    def create(self, vals_list):
        result = super(Partner, self).create(vals_list)
        for res in result:
            seq = self.env['ir.sequence'].next_by_code('customer.code.seq') or '/'
            res.ref = seq
            mail_template_id = self.env.ref('oi_shs_mail.mail_template_new_customer_vendor')    
            self.env['mail.template'].browse(mail_template_id.id).send_mail(res.id, force_send=True)
            
        return result

 
    def action_ledger_send(self):
        for record in self:
            attach_obj = self.env['ir.attachment'].search([('name','=','Partner Ledger.pdf')], limit=1, order='id desc')
            print ("attach_obj")
            mail_template_id = self.env.ref('oi_shs_mail.mail_template_partner_ledger')    
            mail_template_id.attachment_ids = [(6,0,[attach_obj.id])]
            self.env['mail.template'].browse(mail_template_id.id).send_mail(self.id, force_send=True)
            # return True
            ctx = {
            'default_model': 'res.partner',
            'default_template_id': mail_template_id.id,       
            'force_email': True,
            }
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }


class ProductCategory(models.Model):
    _inherit = 'product.category'
    

    @api.model_create_multi
    def create(self, vals_list):
        result = super(ProductCategory, self).create(vals_list)   
        mail_template_id = self.env.ref('oi_shs_mail.mail_template_product_category')    
        self.env['mail.template'].browse(mail_template_id.id).send_mail(self.id, force_send=True)       
        return result

class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    deadline_alert = fields.Boolean('Deadline Alert',default=False, compute='_get_deadline', store=True)

    def _get_deadline(self):
        for record in self:
            record.deadline_alert = ''
            if record.date_deadline:
                deadline = datetime.strptime(str(record.date_deadline), '%Y-%m-%d %H:%M:%S').date()
                diff_date = deadline + timedelta(days=-2)
                alert_date = datetime.strptime(str(diff_date), '%Y-%m-%d').date()
                cur_date = fields.Date.today()
                if cur_date == alert_date:
                    record.deadline_alert = True
                else:
                    record.deadline_alert = False


    def check_for_deadline(self):
        header_label_list=["MO Name" , "Product", "Qty", "Deadline Date"]
        template_obj = self.env['mail.template']    
        template_ids = template_obj.search([('name', '=', 'MO - Deadline Reminder')])[0]
        print ("temppppppppppppp",template_ids)
        default_body = template_ids.body_html
        custom_body  = """
            <table style="border: 1px solid black; width:600px">
                <tr>
                    <th style=width:100px; text-align:center>%s</th>               
                    <th style="text-align:center; width:350px">%s</th>
                    <th style="text-align:center; width:50px">%s</th>
                    <th style="text-align:center; width:100px">%s</th>
                </tr>""" %(header_label_list[0], header_label_list[1], header_label_list[2], header_label_list[3])
        custom_body  += """</table>"""
        mo_search =self.env['mrp.production'].search([('deadline_alert', '=', True)])  
        mo_list_ids=[]
        for mo in mo_search:
            number = str(mo.name)
            product = mo.product_id.name
            qty = str(mo.product_qty)
            date = str(mo.date_deadline)
            print ("mooooooooooo",number, product, qty, date)
            # if min_qty > 0 and forcast < min_qty:
            #     product_list_ids.append(products.name)

            custom_body += """
                <table style="border: 1px solid black; width:500px">

                <tr style="font-size:14px;">
                    <td style=width:100px; text-align:center>%s</td><br/>
                    <td style="text-align:center; width:350px">%s</td><br/>
                    <td style=width:50px; text-align:center>%s</td><br/>
                    <td style="text-align:center; width:100px">%s</td><br/>
                </tr>
            """ %(number,product,qty,date)
            # %(number+ "-" +product+ "-" +qty+ "-" +date)
            custom_body  += "</table>"
        template_ids.body_html=default_body + custom_body
        # template_ids.send_mail(self.id,force_send=True)
        self.env['mail.template'].browse(template_ids.id).send_mail(self.id, force_send=True)       

        template_ids.body_html = default_body
        return True
        

class SaleOrderConfirmation(models.Model):
    _inherit ='sale.order'
    

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

      
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        self.action_sale_send()
        return True


    def action_sale_send(self):
        for record in self:
           
            # mail_template_id = self.env.ref('oi_shs_mail.mail_template_sale_order_confirm')    
            self.ensure_one()
            template_id =self.env.ref('oi_shs_mail.email_template_sale_order_confirm')   
            self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)

            # if template.lang:
            #     lang = template._render_lang(self.ids)[self.id]
            ctx = {
                'default_model': 'sale.order',
                'default_template_id': template_id.id,       
                'force_email': True,
            }
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }
