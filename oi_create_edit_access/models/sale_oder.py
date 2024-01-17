from odoo import api, fields, models, tools, _

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

from odoo.addons.payment import utils as payment_utils


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        if use_invoice_terms and self.env.company.terms_type == "html":
            baseurl = html_keep_url(self._default_note_url() + '/terms')
            context = {'lang': self.partner_id.lang or self.env.user.lang}
            note = _('Terms & Conditions: %s', baseurl)
            del context
            return note
        return use_invoice_terms and self.env.company.invoice_terms or ''
    

    
    def _get_default_require_payment(self):
        return self.env.company.portal_confirmation_pay
    
    def _get_default_require_signature(self):
        return self.env.company.portal_confirmation_sign
    
    def _default_validity_date(self):
        if self.env['ir.config_parameter'].sudo().get_param('sale.use_quotation_validity_days'):
            days = self.env.company.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

   

    #Tracking True for all fields in SO

    origin = fields.Char(string='Source Document', help="Reference of the document that generated this sales order request.",tracking=True)
    client_order_ref = fields.Char(string='Customer Reference', copy=False,tracking=True)
    reference = fields.Char(string='Payment Ref.', copy=False,
        help='The payment communication of this sale order.',tracking=True)
   
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",tracking=True)
    validity_date = fields.Date(string='Expiration', readonly=True, copy=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                default=_default_validity_date,tracking=True)
    is_expired = fields.Boolean(compute='_compute_is_expired', string="Is expired",tracking=True)
    require_signature = fields.Boolean('Online Signature', default=_get_default_require_signature, readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help='Request a online signature to the customer in order to confirm orders automatically.',tracking=True)
    require_payment = fields.Boolean('Online Payment', default=_get_default_require_payment, readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help='Request an online payment to the customer in order to confirm orders automatically.',tracking=True)
    create_date = fields.Datetime(string='Creation Date', readonly=True, index=True, help="Date on which sales order is created.",tracking=True)

    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=True, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=True,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]",)
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True,
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True, ondelete="restrict",tracking=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        compute='_compute_analytic_account_id', store=True,
        readonly=False, copy=False, check_company=True,  # Unrequired company
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="The analytic account related to a sales order.",tracking=True)

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True,tracking=True)

    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced',tracking=True)
    invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", copy=False, search="_search_invoice_ids",tracking=True)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_get_invoice_status', store=True,tracking=True)
    
    
    note = fields.Html('Terms and conditions', default=_default_note,tracking=True)
    terms_type = fields.Selection(related='company_id.terms_type',tracking=True)

    tax_totals_json = fields.Char(compute='_compute_tax_totals_json',tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='_amount_all',tracking=True)
    currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', store=True, digits=(12, 6), help='The rate of the currency to the currency of rate 1 applicable at the date of the order',tracking=True)

    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position',
        domain="[('company_id', '=', company_id)]", check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
        "The default value comes from the customer.",tracking=True)
    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        # Avoid access error on fiscal position when reading a sale order with company != user.company_ids
        compute_sudo=True,
        help="Technical field to filter the available taxes depending on the fiscal country and fiscal position.",tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company,tracking=True)


    signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024,tracking=True)
    signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False,tracking=True)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False,tracking=True)

    commitment_date = fields.Datetime('Delivery Date', copy=False,
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                                      help="This is the delivery date promised to the customer. "
                                           "If set, the delivery order will be scheduled based on "
                                           "this date rather than product lead times.",tracking=True)
    expected_date = fields.Datetime("Expected Date", compute='_compute_expected_date', store=False,  # Note: can not be stored since depends on today()
        help="Delivery date you can promise to the customer, computed from the minimum lead time of the order lines.",tracking=True)
    amount_undiscounted = fields.Float('Amount Before Discount', compute='_compute_amount_undiscounted', digits=0,tracking=True)

    type_name = fields.Char('Type Name', compute='_compute_type_name',tracking=True)

    transaction_ids = fields.Many2many('payment.transaction', 'sale_order_transaction_rel', 'sale_order_id', 'transaction_id',
                                       string='Transactions', copy=False, readonly=True,tracking=True)
    authorized_transaction_ids = fields.Many2many('payment.transaction', compute='_compute_authorized_transaction_ids',
                                                  string='Authorized Transactions', copy=False,tracking=True)
    show_update_pricelist = fields.Boolean(string='Has Pricelist Changed',
                                           help="Technical Field, True if the pricelist was changed;\n"
                                                " this will then display a recomputation button",tracking=True)
    tag_ids = fields.Many2many('crm.tag', 'sale_order_tag_rel', 'order_id', 'tag_id', string='Tags',tracking=True)


    
    

    