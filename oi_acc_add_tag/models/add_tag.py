from odoo import api, fields, models, tools, _



class AddTag(models.Model):
    _inherit = "account.move"

    tag = fields.Many2many('res.partner.category','Tag')


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.category_id:
            self.tag = self.partner_id.category_id
        else:
            self.tag = None

    l10n_in_state_id = fields.Many2one('Location of supply')



class AccountEdiDocumentChanges(models.Model):
    _inherit = "account.edi.document"

    def action_export_xml(self):
       return None






























