from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    activity_state = fields.Char(string='Activity State', compute='_compute_activity_state', store=True)

    @api.depends('activity_ids')
    def _compute_activity_state(self):
        for product in self:
            activities = product.activity_ids.filtered(lambda a: a.state != 'done')
            if activities:
                product.activity_state = ', '.join([a.summary or '' for a in activities])
            else:
                product.activity_state = ''

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model
    def create(self, vals):
        res = super(MailActivity, self).create(vals)
        if res.res_model == 'product.template':
            product = self.env['product.template'].browse(res.res_id)
            product._compute_activity_state()
        return res

    def write(self, vals):
        res = super(MailActivity, self).write(vals)
        if 'res_model' in vals and vals['res_model'] == 'product.template':
            product = self.env['product.template'].browse(vals['res_id'])
            product._compute_activity_state()
        return res

    def unlink(self):
        products = self.filtered(lambda a: a.res_model == 'product.template').mapped('res_id')
        res = super(MailActivity, self).unlink()
        if products:
            product_records = self.env['product.template'].browse(products)
            product_records._compute_activity_state()
        return res