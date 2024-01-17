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
    
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()


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
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, compute='_amount_all', tracking=True)

    tax_totals_json = fields.Char(compute='_compute_tax_totals_json',tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='_amount_all',tracking=True)
    amount_total = fields.Monetary(string='Total', store=True, compute='_amount_all', tracking=True)
    currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', store=True, digits=(12, 6), help='The rate of the currency to the currency of rate 1 applicable at the date of the order',tracking=True)

    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,tracking=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
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

    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        ondelete="set null", tracking=True,
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")



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


    
    
    l10n_in_reseller_partner_id = fields.Many2one('res.partner',
        string='Reseller', domain="[('vat', '!=', False), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},tracking=True)
    l10n_in_journal_id = fields.Many2one('account.journal', string="Journal", compute="_compute_l10n_in_journal_id", store=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},tracking=True)
    l10n_in_gst_treatment = fields.Selection([
            ('regular', 'Registered Business - Regular'),
            ('composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('consumer', 'Consumer'),
            ('overseas', 'Overseas'),
            ('special_economic_zone', 'Special Economic Zone'),
            ('deemed_export', 'Deemed Export'),
        ], string="GST Treatment", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, compute="_compute_l10n_in_gst_treatment", store=True,tracking=True)
    l10n_in_company_country_code = fields.Char(related='company_id.account_fiscal_country_id.code', string="Country code",tracking=True)

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')



    # sale_mrp

    mrp_production_count = fields.Integer(
        "Count of MO generated",
        compute='_compute_mrp_production_count',
        groups='mrp.group_mrp_user',tracking=True)
    
    # #sale_crm

    opportunity_id = fields.Many2one(
        'crm.lead', string='Opportunity', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    

    # sale_stock


    @api.model
    def _default_warehouse_id(self):
        # !!! Any change to the default value may have to be repercuted
        # on _init_column() below.
        return self.env.user._get_default_warehouse_id()

    incoterm = fields.Many2one(
        'account.incoterms', 'Incoterm',
        help="International Commercial Terms are a series of predefined commercial terms used in international transactions.",tracking=True)
    picking_policy = fields.Selection([
        ('direct', 'As soon as possible'),
        ('one', 'When all products are ready')],
        string='Shipping Policy', required=True, readonly=True, default='direct',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
        ,help="If you deliver all products at once, the delivery order will be scheduled based on the greatest "
        "product lead time. Otherwise, it will be based on the shortest.",tracking=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True,tracking=True)
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids',tracking=True)
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False,tracking=True)
    effective_date = fields.Datetime("Effective Date", compute='_compute_effective_date', store=True, help="Completion date of the first delivery order.",tracking=True)
    expected_date = fields.Datetime( help="Delivery date you can promise to the customer, computed from the minimum lead time of "
                                          "the order lines in case of Service products. In case of shipping, the shipping policy of "
                                          "the order will be taken into account to either use the minimum or maximum lead time of "
                                          "the order lines.",tracking=True)
    json_popover = fields.Char('JSON data for the popover widget', compute='_compute_json_popover',tracking=True)
    show_json_popover = fields.Boolean('Has late picking', compute='_compute_json_popover',tracking=True)

    
    # sale_purchase

    purchase_order_count = fields.Integer(
        "Number of Purchase Order Generated",
        compute='_compute_purchase_order_count',
        groups='purchase.group_purchase_user',tracking=True)

    @api.depends('order_line.purchase_line_ids.order_id')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order._get_purchase_orders())

    
    # #sale_management
            
    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quotation Template',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    

    # # sale_project

    tasks_ids = fields.Many2many('project.task', compute='_compute_tasks_ids', string='Tasks associated to this sale',tracking=True)
    tasks_count = fields.Integer(string='Tasks', compute='_compute_tasks_ids', groups="project.group_project_user",tracking=True)

    visible_project = fields.Boolean('Display project', compute='_compute_visible_project', readonly=True,tracking=True)
    project_id = fields.Many2one(
        'project.project', 'Project', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help='Select a non billable project on which tasks can be created.',tracking=True)
    project_ids = fields.Many2many('project.project', compute="_compute_project_ids", string='Projects', copy=False, groups="project.group_project_manager", help="Projects used in this sales order.",tracking=True)
    project_count = fields.Integer(string='Number of Projects', compute='_compute_project_ids', groups='project.group_project_manager',tracking=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    # sale_project

    # project_id = fields.Many2one(
    #     'project.project', 'Generated Project',
    #     index=True, copy=False, help="Project generated by the sales order item",tracking=True)
    # task_id = fields.Many2one(
    #     'project.task', 'Generated Task',
    #     index=True, copy=False, help="Task generated by the sales order item",tracking=True)
    # is_service = fields.Boolean("Is a Service", compute='_compute_is_service', store=True, compute_sudo=True, help="Sales Order item should generate a task and/or a project, depending on the product settings.",tracking=True)


    # # sale_management


    # # sale_purchase

    # purchase_line_count = fields.Integer("Number of generated purchase items", compute='_compute_purchase_count',tracking=True)

    # #sale_stock

    # qty_delivered_method = fields.Selection(selection_add=[('stock_move', 'Stock Moves')],tracking=True)
    # route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)], ondelete='restrict', check_company=True,tracking=True)
    # product_type = fields.Selection(related='product_id.detailed_type',tracking=True)
    # virtual_available_at_date = fields.Float(compute='_compute_qty_at_date', digits='Product Unit of Measure',tracking=True)
    # scheduled_date = fields.Datetime(compute='_compute_qty_at_date',tracking=True)
    # forecast_expected_date = fields.Datetime(compute='_compute_qty_at_date',tracking=True)
    # free_qty_today = fields.Float(compute='_compute_qty_at_date', digits='Product Unit of Measure',tracking=True)
    # qty_available_today = fields.Float(compute='_compute_qty_at_date',tracking=True)
    # warehouse_id = fields.Many2one(related='order_id.warehouse_id',tracking=True)
    # qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver', digits='Product Unit of Measure',tracking=True)
    # is_mto = fields.Boolean(compute='_compute_is_mto',tracking=True)
    # display_qty_widget = fields.Boolean(compute='_compute_qty_to_deliver',tracking=True)


    # #sale


    # order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False,tracking=True)
    # name = fields.Text(string='Description', required=True,tracking=True)

    # invoice_lines = fields.Many2many('account.move.line', 'sale_order_line_invoice_rel', 'order_line_id', 'invoice_line_id', string='Invoice Lines', copy=False,tracking=True)
    # invoice_status = fields.Selection([
    #     ('upselling', 'Upselling Opportunity'),
    #     ('invoiced', 'Fully Invoiced'),
    #     ('to invoice', 'To Invoice'),
    #     ('no', 'Nothing to Invoice')
    #     ], string='Invoice Status', compute='_compute_invoice_status', store=True, default='no',tracking=True)
    # price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0,tracking=True)

    # price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True,tracking=True)
    # price_tax = fields.Float(compute='_compute_amount', string='Total Tax', store=True,tracking=True)
    # price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True,tracking=True)

    # price_reduce = fields.Float(compute='_compute_price_reduce', string='Price Reduce', digits='Product Price', store=True,tracking=True)
    # tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False}, check_company=True,tracking=True)
    # price_reduce_taxinc = fields.Monetary(compute='_compute_price_reduce_taxinc', string='Price Reduce Tax inc', store=True,tracking=True)
    # price_reduce_taxexcl = fields.Monetary(compute='_compute_price_reduce_taxexcl', string='Price Reduce Tax excl', store=True,tracking=True)

    # discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0,tracking=True)

    # product_id = fields.Many2one(
    #     'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    #     change_default=True, ondelete='restrict', check_company=True,tracking=True)  # Unrequired company
    # product_template_id = fields.Many2one(
    #     'product.template', string='Product Template',
    #     related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)],tracking=True)
    # product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', default=True,tracking=True)
    # product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0,tracking=True)
    # product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict",tracking=True)
    # product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id',tracking=True)
    # product_uom_readonly = fields.Boolean(compute='_compute_product_uom_readonly',tracking=True)

    # # M2M holding the values of product.attribute with create_variant field set to 'no_variant'
    # # It allows keeping track of the extra_price associated to those attribute values and add them to the SO line description
    # product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values", ondelete='restrict',tracking=True)

    # qty_delivered_method = fields.Selection([
    #     ('manual', 'Manual'),
    #     ('analytic', 'Analytic From Expenses')
    # ], string="Method to update delivered qty", compute='_compute_qty_delivered_method', store=True,
    #     help="According to product configuration, the delivered quantity can be automatically computed by mechanism :\n"
    #          "  - Manual: the quantity is set manually on the line\n"
    #          "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
    #          "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
    #          "  - Stock Moves: the quantity comes from confirmed pickings\n",tracking=True)
    # qty_delivered = fields.Float('Delivered Quantity', copy=False, compute='_compute_qty_delivered', inverse='_inverse_qty_delivered', store=True, digits='Product Unit of Measure', default=0.0,tracking=True)
    # qty_delivered_manual = fields.Float('Delivered Manually', copy=False, digits='Product Unit of Measure', default=0.0,tracking=True)
    # qty_to_invoice = fields.Float(
    #     compute='_get_to_invoice_qty', string='To Invoice Quantity', store=True,
    #     digits='Product Unit of Measure',tracking=True)
    # qty_invoiced = fields.Float(
    #     compute='_compute_qty_invoiced', string='Invoiced Quantity', store=True,
    #     digits='Product Unit of Measure',tracking=True)

    # untaxed_amount_invoiced = fields.Monetary("Untaxed Invoiced Amount", compute='_compute_untaxed_amount_invoiced', store=True,tracking=True)
    # untaxed_amount_to_invoice = fields.Monetary("Untaxed Amount To Invoice", compute='_compute_untaxed_amount_to_invoice', store=True,tracking=True)

    # salesman_id = fields.Many2one(related='order_id.user_id', store=True, string='Salesperson',tracking=True)
    # currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency',tracking=True)
    # company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, index=True,tracking=True)
    # order_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer', index=True,tracking=True)
    # analytic_tag_ids = fields.Many2many(
    #     'account.analytic.tag', string='Analytic Tags',
    #     compute='_compute_analytic_tag_ids', store=True, readonly=False,
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    # is_expense = fields.Boolean('Is expense', help="Is true if the sales order line comes from an expense or a vendor bills",tracking=True)
    # is_downpayment = fields.Boolean(
    #     string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
    #     " They are not copied when duplicating a sales order.",tracking=True)

    # state = fields.Selection(
    #     related='order_id.state', string='Order Status', copy=False, store=True,tracking=True)

    # customer_lead = fields.Float(
    #     'Lead Time', required=True, default=0.0,
    #     help="Number of days between the order confirmation and the shipping of the products to the customer",tracking=True)

    # display_type = fields.Selection([
    #     ('line_section', "Section"),
    #     ('line_note', "Note")], default=False, help="Technical field for UX purpose.",tracking=True)

    # product_packaging_id = fields.Many2one('product.packaging', string='Packaging', default=False, domain="[('sales', '=', True), ('product_id','=',product_id)]", check_company=True,tracking=True)
    # product_packaging_qty = fields.Float('Packaging Quantity',tracking=True)