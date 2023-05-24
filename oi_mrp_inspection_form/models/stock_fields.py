# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
#
from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import json
from odoo.exceptions import UserError, ValidationError


class stock_picking_inherit(models.Model):
    _inherit = 'mrp.production'



    def action_view_inspection(self):

        print("action ??????????????????????????/")
        ins_ids = []
        action = self.env.ref('oi_mrp_inspection_form.mrp_quality_inspection_form_action').read()[0]
        print("action =================",action)
        ins_search = self.env['mrp.quality.inspection'].search([])
        for data in ins_search:
            ins_ids.append(data.id)
            print("ins_ids ========================",ins_ids)
        action['domain'] = [('id','in',ins_ids)]
        return action

class qualityInspection(models.Model):
    _inherit = 'quality.inspection'

class MrpInspection(models.Model):
    _name = 'mrp.quality.inspection'

    # mo_no = fields.Char('Mo Number')
    mo_no = fields.Many2one('mrp.production','Mo Number')
    partner_id = fields.Many2one('res.partner','Partner')
    product_id = fields.Many2one('product.product', 'Product')
    categ_id = fields.Many2one('product.category','Category',related='product_id.categ_id',store=True)
    date = fields.Date('Date')
    shift = fields.Char('Shift')
    total_quantity = fields.Float('Total quantity')
    sample_quantity = fields.Float('Sample Quantity')
    msn_rej_quantity = fields.Float('MSN Rejection Quantity')
    inprogress_rej_quantity = fields.Float('Inprogress Rejection Quantity')
    # template_id = fields.Many2one('inspection.template','Template')
    template_id = fields.Many2one('inspection.template','Template')
    # inspection_line_ids = fields.One2many('inspection.line','inspec_line_id','Lines')
    # inspection1_line_ids = fields.One2many('inspection.line.char','inspec_line_char_id','Lines')
    inspection_line_ids = fields.One2many('inspection.line','inspec_line_id','Lines')
    inspection1_line_ids = fields.One2many('inspection.line.char','inspec_line_char_id','Lines')
    
    accepted_quantity = fields.Float('Accepted Quantity')
    operation_name = fields.Char('Operation Name')
    op_sup_name = fields.Char('Operator/Supplier Name')
    pro_draw_no = fields.Char('Product Drawing Number')
    insp_date = fields.Date('Inspected Date',default=fields.Date.context_today)
    total_rej_quantity = fields.Float('Total Rejection Quantity')
    msn_rej_description = fields.Char('MSN Rejection Description')
    in_rej_description = fields.Char('Inprogress Rejection Description')
    inspected_by = fields.Char('Inspected By')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled')
    ], string='Status',copy=False, index=True, readonly=True, store=True,track_visibility='onchange',default="draft")

    name = fields.Char('Inspection No.',default=lambda self: _(' '),readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _(' ')) == _(' '):
           
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.quality.inspection') or _(' ')
        result = super(MrpInspection, self).create(vals)
        return result


    # @api.multi
    def write(self, values):
        print(values, "]]]]]]]]]")
        res = super(MrpInspection, self).write(values)
        # if values:
        #     self.mo_no.write({'inspection_status': 'complete'})
        return res
    
    @api.onchange('mo_no')
    def onchange_mo_no(self):
        product_ids_list = []
        if self.mo_no:
            for line in self.mo_no.move_raw_ids:
            
                product_ids_list.append(line.product_id.id)

        return {'domain':{'product_id':[('id','in',product_ids_list)]}}
  

    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise UserError(_('You can not delete confirmed entry. You must first cancel it.'))
        return super(MrpInspection, self).unlink()
    
    def action_confirm(self):
        for record in self:
            record.write({'state':'confirm'})
            # record.mo_no.write({'inspection_status':'complete'})

    # @api.multi
    def action_cancel(self):
        for record in self:
            record.write({'state':'cancel'})

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            for line in self.mo_no.move_raw_ids:
                if self.product_id.id == line.product_id.id:
                    self.total_quantity = line.quantity_done
                   
 
    @api.onchange('template_id')
    def onchange_template_id(self):
        template = self.template_id.with_context(lang=self.partner_id.lang)
        inspection_lines = []
        for line in template.template_line_ids:
            data = {}
            if line.dimension:

                data.update({

                        'dimension': line.dimension,
                        'values':line.values,
                        'range_one': line.range_one,
                        'range_two': line.range_two,
                        'inspection_method': line.inspection_method,
                        'inspec_line_id': self.id
                    })
            inspection_lines.append(data)
        print(inspection_lines)
        for rec in inspection_lines:
            il = self.env['inspection.line'].create(rec)

       

        inspection1_lines = []
        for l in template.template1_line_ids:
            data = {}
            if l.dimension:

                data.update({

                        'dimension': l.dimension,
                        'values':l.values,
                        'range_one': l.range_one,
                        'range_two': l.range_two,
                        'inspection_method': l.inspection_method,
                        'inspec_line_id':self.id
                    })
            inspection1_lines.append(data)
        for rec1 in inspection1_lines:
            il1 = self.env['inspection.line'].create(rec1)


    # @api.onchange('template_id')
    # def onchange_template_id(self):
    #     template = self.template_id.with_context(lang=self.partner_id.lang)
    #     inspection_lines = [(5, 0, 0)]
    #     for line in template.template_line_ids:
    #         data = {}
    #         if line.dimension:

    #             data.update({

    #                     'dimension': line.dimension,
    #                     'values':line.values,
    #                     'range_one': line.range_one,
    #                     'range_two': line.range_two,
    #                     'inspection_method': line.inspection_method
    #                 })
    #         inspection_lines.append((0, 0, data))
    #     self.inspection_line_ids = inspection_lines
    #     inspection1_lines = [(5, 0, 0)]
    #     for l in template.template1_line_ids:
    #         data = {}
    #         if l.dimension:

    #             data.update({

    #                     'dimension': l.dimension,
    #                     'values':l.values,
    #                     'range_one': l.range_one,
    #                     'range_two': l.range_two,
    #                     'inspection_method': l.inspection_method
    #                 })
    #         inspection1_lines.append((0, 0, data))
    #     self.inspection1_line_ids = inspection1_lines

        

    def action_update_status(self):
        for rec in self:
            for line in rec.inspection_line_ids:
                if line.range_one and line.range_two:
                    if line.s1 <= line.range_two and line.s1 >= line.range_one and line.s2 <= line.range_two and line.s2 >= line.range_one and line.s3 <= line.range_two and line.s3 >= line.range_one and line.s4 <= line.range_two and line.s4 >= line.range_one and line.s5 <= line.range_two and line.s5 >= line.range_one:
                        line.state='accept'
                    
                    else:
                        line.state='reject'
                if line.range_one == 0 and line.s1 ==0 and line.s2==0 and line.s3==0 and line.s4==0 and line.s5==0:
                    line.state='reject'
                if line.range_one ==0 and line.range_two > 0:
                    if line.s1 <= line.range_two and line.s1 >= line.range_one and line.s2 <= line.range_two and line.s2 >= line.range_one and line.s3 <= line.range_two and line.s3 >= line.range_one and line.s4 <= line.range_two and line.s4 >= line.range_one and line.s5 <= line.range_two and line.s5 >= line.range_one:
                        line.state='accept'
                    
                    else:
                        line.state='reject'


class inspection_line(models.Model):
    _name = 'inspection.line'

    inspection_line_id=fields.Many2one('quality.inspection','Template')
    inspec_line_id = fields.Many2one('mrp.quality.inspection','Template')
    dimension = fields.Char('Description',readonly=True)
    values = fields.Char('Specification',readonly=True)
    range_one = fields.Float('Min',readonly=True)
    range_two = fields.Float('Max',readonly=True)
    inspection_method = fields.Char('Inspection Method',readonly=True)
    s1 = fields.Float('S1')
    # s1_bool = fields.Boolean('S1 Bool',default=False)
    s2 = fields.Float('S')
    s3 = fields.Float('S')
    s4 = fields.Float('S')
    s5 = fields.Float('S')
    
    remarks = fields.Char('Remarks')
    state = fields.Selection([
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ], string='Status',copy=False)
    # status = fieds.Char('Status')


class inspection_line_char(models.Model):
    _name = 'inspection.line.char'

    inspection_line_char_id=fields.Many2one('quality.inspection','Template')
    inspec_line_char_id=fields.Many2one('mrp.quality.inspection','Template')
    dimension = fields.Char('Description',readonly=True)
    values = fields.Char('Specification',readonly=True)
    range_one = fields.Char('Min',readonly=True)
    range_two = fields.Char('Max',readonly=True)
    inspection_method = fields.Char('Inspection Method',readonly=True)
    s1 = fields.Float('S1')
    # s1_bool = fields.Boolean('S1 Bool',default=False)
    s2 = fields.Float('S')
    s3 = fields.Float('S')
    s4 = fields.Float('S')
    s5 = fields.Float('S')
    
    remarks = fields.Char('Remarks')
    state = fields.Selection([
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ], string='Status',copy=False)
    # status = fieds.Char('Status')

