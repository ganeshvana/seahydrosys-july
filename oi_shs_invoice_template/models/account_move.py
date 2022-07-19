# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type
        """
        return (
            'account.email_template_edi_credit_note'
            if all(move.move_type == 'out_refund' for move in self)
            else 'oi_shs_invoice_template.email_template_edi_invoice_custom'
        )

