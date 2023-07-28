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

    
class quality_inspection_out(models.Model):
    _name = 'quality.inspection.out'
    _inherit = ['mail.thread']
  

    name = fields.Char('Inspection No.',default=lambda self: _(' '),readonly=True)
    picking_id = fields.Many2one('stock.picking','Out No.')
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_id.picking_type_id.code',
        readonly=True)
    # operation_name=fields.Char('Operation Name')
    product_id = fields.Many2one('product.product', 'Product')
    categ_id = fields.Many2one('product.category','Category',related='product_id.categ_id',store=True)

    description = fields.Char('Description',readonly=True)

    wo_no = fields.Char('WO No.')
    sl_no_from = fields.Char('Part SL No.From')
    sl_no_to = fields.Char('Part SL No.To')

    partner_id = fields.Many2one('res.partner','Customer')
    deliver_date = fields.Datetime('Delivery Date')
    inspection_qty = fields.Float('Inspection Qty')
    # total_qty = fields.Float('Total Qty',readonly=True)
    inv_no_date = fields.Char('INV No & Date')
    po_no = fields.Char('Purchase Order Number')
    scheduled_date = fields.Datetime('Scheduled Date',readonly=True)

   
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))

    drawing_no = fields.Char('Drawing No',readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled')
    ], string='Status',copy=False, index=True, readonly=True, store=True,track_visibility='onchange',default="draft")
    inspection_date = fields.Date('Inspection Date')
    defect_remarks = fields.Char('Defect Remarks')

    lot_qty = fields.Float('Lot Qty')
    inspected_by = fields.Many2one('hr.employee','Employee')
    out_template_id = fields.Many2one('inspection.template.out','Out Template')
    out_inspection_line_ids = fields.One2many('out.inspection.line','out_inspection_line_id','Lines')
    out_inspection1_line_ids = fields.One2many('out.inspection.line.char','out_inspection_line_char_id','Lines')

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
    # rejection_reference = fields.Char("Rejection Reference")

    


    @api.model
    def create(self, vals):
        if vals.get('name', _(' ')) == _(' '):
            # if 'company_id' in vals:
            #     vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
            # else:
            vals['name'] = self.env['ir.sequence'].next_by_code('quality.inspection.out') or _(' ')
        result = super(quality_inspection_out, self).create(vals)
        return result



    @api.onchange('picking_id')
    def onchange_picking_id(self):
        product_ids_list = []
        if self.picking_id:
            for line in self.picking_id.move_ids_without_package:
            
                product_ids_list.append(line.product_id.id)
            if self.picking_id.partner_id.id:
                self.partner_id = self.picking_id.partner_id.id
            if self.picking_id.vendor.id:
                self.partner_id = self.picking_id.vendor.id
            self.deliver_date = self.picking_id.date_done
            self.inv_no_date = self.picking_id.supplier_ref
            self.po_no = self.picking_id.buyer_order_no
            self.scheduled_date = self.picking_id.scheduled_date
            self.drawing_no = self.picking_id.drawing_no

        return {'domain':{'product_id':[('id','in',product_ids_list)]}}


    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise UserError(_('You can not delete confirmed entry. You must first cancel it.'))
        return super(quality_inspection_out, self).unlink()

    def action_confirm(self):
        for record in self:
            record.write({'state':'confirm'})
            record.picking_id.write({'out_inspection_status':'complete'})

    def action_cancel(self):
        for record in self:
            record.write({'state':'cancel'})


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            for line in self.picking_id.move_ids_without_package:
                if self.product_id.id == line.product_id.id:
                    self.description = line.name


    def action_update_status(self):
        for rec in self:
            for line in rec.out_inspection_line_ids:
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


    

    @api.onchange('out_template_id')
    def onchange_template_id(self):
        template = self.out_template_id.with_context(lang=self.partner_id.lang)
        inspection_lines = [(5, 0, 0)]
        for line in template.out_template_line_ids:
            data = {}
            if line.description:

                data.update({
                        
                        'description': line.description,
                        'specification':line.specification,
                        # 'tolerance': line.tolerance,
                        'range_one':line.range_one,
                        'range_two': line.range_two,
                        'inspection_method': line.inspection_method
                    })
            inspection_lines.append((0, 0, data))
        self.out_inspection_line_ids = inspection_lines
        inspection1_lines = [(5, 0, 0)]
        for l in template.out_template1_line_ids:
            data = {}
            if l.description:

                data.update({
                        
                        'description': l.description,
                        'specification':l.specification,
                        # 'tolerance': line.tolerance,
                        'range_one':l.range_one,
                        'range_two': l.range_two,
                        'inspection_method': l.inspection_method
                    })
            inspection1_lines.append((0, 0, data))
        self.out_inspection1_line_ids = inspection1_lines



class out_inspection_line(models.Model):
    _name = 'out.inspection.line'

    out_inspection_line_id=fields.Many2one('quality.inspection.out','Out Template')
    description = fields.Char('Description',readonly=True)
    specification = fields.Char('Specification',readonly=True)
    # tolerance = fields.Float('Tolerance',readonly=True)
    range_one = fields.Float('Min',readonly=True)
    range_two = fields.Float('Max',readonly=True)
    inspection_method = fields.Char('Inspection Method',readonly=True)
    s1 = fields.Float('1')
    s2 = fields.Float('2')
    s3 = fields.Float('3')
    s4 = fields.Float('4')
    s5 = fields.Float('5')
    
    remarks = fields.Char('Remarks')
    state = fields.Selection([
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ], string='Status',copy=False)
    # status = fieds.Char('Status')


class out_inspection_line_char(models.Model):
    _name = 'out.inspection.line.char'

    out_inspection_line_char_id=fields.Many2one('quality.inspection.out','Out Template')
    description = fields.Char('Description',readonly=True)
    specification = fields.Char('Specification',readonly=True)
    # tolerance = fields.Float('Tolerance',readonly=True)
    range_one = fields.Float('Min',readonly=True)
    range_two = fields.Float('Max',readonly=True)
    inspection_method = fields.Char('Inspection Method',readonly=True)
    s1 = fields.Float('1')
    s2 = fields.Float('2')
    s3 = fields.Float('3')
    s4 = fields.Float('4')
    s5 = fields.Float('5')
    
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

    out_inspection_status = fields.Selection([
        ('pending', 'Pending'),
        ('complete', 'Completed'),
    ], string='Out Inspection Status',copy=False,default="pending")

    


    

  



    
    
        
