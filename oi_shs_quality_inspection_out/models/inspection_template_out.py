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
    
class inspection_template_out(models.Model):
    _name = 'inspection.template.out'
  

    name = fields.Char('Template Name')
    out_template_line_ids = fields.One2many('inspection.template.out.line','out_template_line_id','Lines')
    out_template1_line_ids = fields.One2many('inspection.template.out.line.char','out_template_line_char_id','Lines')


class inspection_template_out_line(models.Model):
    _name = 'inspection.template.out.line'

    out_template_line_id=fields.Many2one('inspection.template.out','Template')
    description = fields.Char('Description')
    specification = fields.Char('Specification')
    range_one = fields.Float('Min')
    range_two = fields.Float('Max')

    # tolerance = fields.Float('Tolerance')
    # range_two = fields.Char('Range2')
    inspection_method = fields.Char('Inspection Method')


class inspection_template_out_line_char(models.Model):
    _name = 'inspection.template.out.line.char'

    out_template_line_char_id=fields.Many2one('inspection.template.out','Template')
    description = fields.Char('Description')
    specification = fields.Char('Specification')
    range_one = fields.Char('Min')
    range_two = fields.Char('Max')

    # tolerance = fields.Float('Tolerance')
    # range_two = fields.Char('Range2')
    inspection_method = fields.Char('Inspection Method')



   

    
    
        
