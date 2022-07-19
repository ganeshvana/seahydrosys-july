from odoo import api, fields, models, _
import logging


_logger = logging.getLogger(__name__)


class TaskInherit(models.Model):
    _inherit = "project.task"

    # employee_id  = fields.Many2one('hr.employee',string="Employee")
    sale_ids = fields.Many2many('sale.order',string='Sale')
    purchase_ids = fields.Many2many('purchase.order',string='Purchase')
    mrp_ids = fields.Many2many('mrp.production',string='MO')




    
    
    
    

