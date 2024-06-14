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
from odoo.exceptions import UserError, ValidationError

    
class quality_inspection(models.Model):
    _name = 'quality.inspection'
    _inherit = ['mail.thread']
  

    name = fields.Char('Inspection No.',default=lambda self: _(' '),readonly=True)
    picking_id = fields.Many2one('stock.picking','GRN No.')
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_id.picking_type_id.code',
        readonly=True)
    operation_name=fields.Char('Operation Name')
    product_id = fields.Many2one('product.product', 'Product')
    categ_id = fields.Many2one('product.category','Category',related='product_id.categ_id',store=True)
    description = fields.Char('Description',readonly=True)
    partner_id = fields.Many2one('res.partner','Partner')
    grn_date = fields.Datetime('GRN Date')
    scheduled_date = fields.Datetime('Scheduled Date',readonly=True)
    sample_qty = fields.Float('Sample Qty')
    total_qty = fields.Float('Total Qty',readonly=True)
    inv_no_date = fields.Char('INV No & Date')
    defect_remarks = fields.Char('Defect Remarks')
    supplier_test = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'NA'),

    ], string='RM Test Certificate')

    corrective_test = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'NA'),

    ], string='Corrective Action Report')
    supplier_inspection = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'NA'),

    ], string='Supplier Inspection Report')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    corrective_action = fields.Char('Corrective Action')
    # drawing_no_id = fields.Many2one('drawing.master','Drawing No')
    drawing_no = fields.Char('Drawing No')
    defect_type_id = fields.Many2one('defect.type.master','Type of Defect')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled')
    ], string='Status',copy=False, index=True, readonly=True, store=True,track_visibility='onchange',default="draft")
    shift = fields.Char('Shift')
    inspection_date = fields.Date('Inspection Date')
    rejection_qty = fields.Float('Rejection Qty')
    inspected_by = fields.Many2one('hr.employee','Employee')
    template_id = fields.Many2one('inspection.template','Template')
    inspection_line_ids = fields.One2many('inspection.line','inspection_line_id','Lines')
    inspection1_line_ids = fields.One2many('inspection.line.char','inspection_line_char_id','Lines')

    result = fields.Selection([
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ], string='Result',copy=False)
    osn_qty = fields.Float('OSN Rejection Qty')
    osn_description = fields.Char('OSN Rejection Description')
    msn_qty = fields.Float('MSN Rejection Qty')
    msn_description = fields.Char('MSN Rejection Description')
    process_qty = fields.Float('Process Rejection Qty')
    process_description = fields.Char('process Rejection Description')
    rm_supplier_id = fields.Many2one('res.partner','RM Supplier')
    rejection_reference = fields.Char("Rejection Reference")
    debit_note_reference = fields.Char("Debit Note Reference")

    @api.onchange('osn_qty','msn_qty','process_qty')
    def compute_rejection_qty(self):
        for rec in self:
            if rec.osn_qty or rec.msn_qty or rec.process_qty:
                rec.rejection_qty = rec.osn_qty+rec.msn_qty+rec.process_qty
            else:
                rec.rejection_qty = 0.00    
                

    @api.model
    def create(self, vals):
        if vals.get('name', _(' ')) == _(' '):
           
            vals['name'] = self.env['ir.sequence'].next_by_code('quality.inspection') or _(' ')
        result = super(quality_inspection, self).create(vals)
        return result


    # @api.multi
    def write(self, values):
        res = super(quality_inspection, self).write(values)
        if values:
            self.picking_id.write({'inspection_status': 'complete'})
        return res

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        product_ids_list = []
        if self.picking_id:
            for line in self.picking_id.move_ids_without_package:
            
                product_ids_list.append(line.product_id.id)
                # self.description = line.name
            if self.picking_id.partner_id.id:
                self.partner_id = self.picking_id.partner_id.id
            if self.picking_id.vendor.id:
                self.partner_id = self.picking_id.vendor.id

            self.grn_date = self.picking_id.date_done
            self.inv_no_date = self.picking_id.supplier_ref
            self.scheduled_date = self.picking_id.scheduled_date
            self.drawing_no = self.picking_id.drawing_no


        return {'domain':{'product_id':[('id','in',product_ids_list)]}}

    # @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise UserError(_('You can not delete confirmed entry. You must first cancel it.'))
        return super(quality_inspection, self).unlink()

    # @api.multi
    def action_confirm(self):
        for record in self:
            record.write({'state':'confirm'})
            record.picking_id.write({'inspection_status':'complete'})

    # @api.multi
    def action_cancel(self):
        for record in self:
            record.write({'state':'cancel'})


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            for line in self.picking_id.move_ids_without_package:
                if self.product_id.id == line.product_id.id:
                    self.total_qty = line.quantity_done
                    self.description = line.name
    

    @api.onchange('template_id')
    def onchange_template_id(self):
        template = self.template_id.with_context(lang=self.partner_id.lang)
        inspection_lines = [(5, 0, 0)]
        for line in template.template_line_ids:
            data = {}
            if line.dimension:

                data.update({

                        'dimension': line.dimension,
                        'values':line.values,
                        'range_one': line.range_one,
                        'range_two': line.range_two,
                        'inspection_method': line.inspection_method
                    })
            inspection_lines.append((0, 0, data))
        self.inspection_line_ids = inspection_lines
        inspection1_lines = [(5, 0, 0)]
        for l in template.template1_line_ids:
            data = {}
            if l.dimension:

                data.update({

                        'dimension': l.dimension,
                        'values':l.values,
                        'range_one': l.range_one,
                        'range_two': l.range_two,
                        'inspection_method': l.inspection_method
                    })
            inspection1_lines.append((0, 0, data))
        self.inspection1_line_ids = inspection1_lines


    # @api.multi
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


    


class defect_type_master(models.Model):
    _name = 'defect.type.master'

    name = fields.Char('Name')
    code = fields.Char('Code')


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    inspection_status = fields.Selection([
        ('pending', 'Pending'),
        ('complete', 'Completed'),
    ], string='Inspection Status',copy=False,default="pending")
    
    # user_id =fields.Many2one('res.users',compute='_compute_responsible',store=True)
    
    # @api.depends('origin')
    # def _compute_responsible(self):
    #     for rec in self:
    #         if rec.picking_type_code = "incoming" and rec.origin:
    #            check_user = self.env['purchase.order'].search([('name','=',rec.origin)],limit=1)
    #             if check_user:
    #                rec.user_id = check_user.user_id.id  
    #             else:
    #                  rec.user_id = None   

    


    

  



    
    
        
