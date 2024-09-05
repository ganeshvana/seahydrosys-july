# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    lead_product_ids = fields.One2many('lead.line', 'lead_line_id', string='Products', copy=True)
    crm_count = fields.Integer(string="Quotation",compute="get_quotation_count")
    is_crm_quotation = fields.Boolean('Is CRM Quotation')
    is_lost = fields.Boolean(related='stage_id.is_lost',string="Lost")
    machine_type = fields.Char(string="Machine Type")

    
    def action_set_lost(self, **additional_values):
        """ Lost semantic: probability = 0 or active = False """
        if additional_values:
            self.write(dict(additional_values))
        return True

    def action_quotations_view(self):
        order_line = [] 
        for record in self.lead_product_ids:  
            order_line.append((0, 0, {
                                     'product_id'     : record.product_id.id,
                                     'name'           : record.name, 
                                     'product_uom_qty': record.product_uom_quantity,
                                     'price_unit'     : record.price_unit,
                                     'tax_id'        : [(6, 0, record.tax_id.ids)],
                                }))
        
        sale_obj = self.env['sale.order']
        if self.partner_id:
            for record in self.lead_product_ids:  
                if record.product_id and record.name:
                    sale_create_obj = sale_obj.create({
                                    'partner_id': self.partner_id.id,
                                    'opportunity_id': self.id,
                                    'state': "draft",
                                    'order_line': order_line,
                                    })
                return {
                    'name': "Sale Order",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': self.env.ref('sale.view_order_form').id,
                    'target': "new",
                    'res_id': sale_create_obj.id
                }
            else:
                raise UserError('Enter the "Product" and "Description".')
        else:
            raise UserError('Please select the "Customer".')             



    def open_quotation_from_view_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('partner_id','=',self.partner_id.id),('opportunity_id','=',self.id)]
        return action


    def get_quotation_count(self):
        count = self.env['sale.order'].search_count([('partner_id','=',self.partner_id.id),('opportunity_id','=',self.id)])
        self.crm_count = count




   
class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'
    
    
    lost_reason_id = fields.Many2one('crm.lost.reason', 'Lost Reason') 
    
    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        # Find the stage where is_lost is True
        lost_stage = self.env['crm.stage'].search([('is_lost', '=', True)], limit=1)
        if lost_stage:
            leads.write({'stage_id': lost_stage.id})
        return leads.action_set_lost(lost_reason=self.lost_reason_id.id)
    
  
    
    
class CRMStage(models.Model):
    _inherit = 'crm.stage'
    
    is_lost  = fields.Boolean("")
    
    
    
    