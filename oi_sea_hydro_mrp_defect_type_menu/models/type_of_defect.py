from odoo import models,fields,api


class DefectTypes(models.Model):
    _name="defect.type"
    _description="Type of defects"

    name = fields.Char("Name")
    