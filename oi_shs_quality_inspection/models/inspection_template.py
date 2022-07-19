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
    
class inspection_template(models.Model):
    _name = 'inspection.template'
  

    name = fields.Char('Template Name')
    template_line_ids = fields.One2many('inspection.template.line','template_line_id','Lines')
    template1_line_ids = fields.One2many('inspection.template.line.char','template_line_char_id','Lines')




class inspection_template_line(models.Model):
    _name = 'inspection.template.line'

    template_line_id=fields.Many2one('inspection.template','Template')
    dimension = fields.Char('Dimension Per Drawing')
    values = fields.Char('Values')
    range_one = fields.Float('Range1')
    range_two = fields.Float('Range2')
    inspection_method = fields.Char('Inspection Method')

class inspection_template_line_char(models.Model):
    _name = 'inspection.template.line.char'

    template_line_char_id=fields.Many2one('inspection.template','Template')
    dimension = fields.Char('Dimension Per Drawing')
    values = fields.Char('Values')
    range_one = fields.Char('Range1')
    range_two = fields.Char('Range2')
    inspection_method = fields.Char('Inspection Method')

   

    
    
        
