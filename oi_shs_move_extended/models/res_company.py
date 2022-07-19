from odoo import api, fields, models, _

class res_company(models.Model):
	_inherit = 'res.company'

	cin_no = fields.Char('CIN No')
	ie_code = fields.Char('IE Code')
	ad_code = fields.Char('AD Code')

