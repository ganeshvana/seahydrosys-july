from odoo import api, fields, models, tools, _
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    #purchase 

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New',tracking=True)
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True,tracking=True)
    origin = fields.Char('Source Document', copy=False,
        help="Reference of the document that generated this purchase order "
             "request (e.g. a sales order)",tracking=True)
    partner_ref = fields.Char('Vendor Reference', copy=False,
        help="Reference of the sales order or bid sent by the vendor. "
             "It's used to do the matching when you receive the "
             "products as this reference is usually written on the "
             "delivery order sent by your vendor.",tracking=True)
    date_order = fields.Datetime('Order Deadline', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now,
        help="Depicts the date within which the Quotation should be confirmed and converted into a purchase order.",tracking=True)
    date_approve = fields.Datetime('Confirmation Date', readonly=1, index=True, copy=False,tracking=True)
    dest_address_id = fields.Many2one('res.partner', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", string='Dropship Address', states=READONLY_STATES,
        help="Put an address if you want to deliver directly from the vendor to the customer. "
             "Otherwise, keep empty to deliver to your own company.",tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES,
        default=lambda self: self.env.company.currency_id.id,tracking=True)
   
    notes = fields.Html('Terms and Conditions',tracking=True)

    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True,tracking=True)
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True,tracking=True)
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
    ], string='Billing Status', compute='_get_invoiced', store=True, readonly=True, copy=False, default='no',tracking=True)
    date_planned = fields.Datetime(
        string='Receipt Date', index=True, copy=False, compute='_compute_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.",tracking=True)
    date_calendar_start = fields.Datetime(compute='_compute_date_calendar_start', readonly=True, store=True,tracking=True)

    # tax_totals_json = fields.Char(compute='_compute_tax_totals_json',tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',tracking=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',tracking=True)

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        # Avoid access error on fiscal position, when reading a purchase order with company != user.company_ids
        compute_sudo=True,
        help="Technical field to filter the available taxes depending on the fiscal country and fiscal position.",tracking=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', states={'done': [('readonly', True)]}, help="International Commercial Terms are a series of predefined commercial terms used in international transactions.",tracking=True)

    product_id = fields.Many2one('product.product', related='order_line.product_id', string='Product',tracking=True)
   
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.company.id,tracking=True)
    currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', compute_sudo=True, store=True, readonly=True, help='Ratio between the purchase order currency and the company currency',tracking=True)

    mail_reminder_confirmed = fields.Boolean("Reminder Confirmed", default=False, readonly=True, copy=False, help="True if the reminder email is confirmed by the vendor.",tracking=True)
    mail_reception_confirmed = fields.Boolean("Reception Confirmed", default=False, readonly=True, copy=False, help="True if PO reception is confirmed by the vendor.",tracking=True)

    receipt_reminder_email = fields.Boolean('Receipt Reminder Email', related='partner_id.receipt_reminder_email', readonly=False,tracking=True)
    reminder_date_before_receipt = fields.Integer('Days Before Receipt', related='partner_id.reminder_date_before_receipt', readonly=False,tracking=True)

    #purchase requsition

    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Agreement', copy=False,tracking=True)
    is_quantity_copy = fields.Selection(related='requisition_id.is_quantity_copy', readonly=False,tracking=True)

    #mrp_subcontracting_purchase

    subcontracting_resupply_picking_count = fields.Integer(
        "Count of Subcontracting Resupply", compute='_compute_subcontracting_resupply_picking_count',
        help="Count of Subcontracting Resupply for component",tracking=True)
    

    #l10n_in_purchase

    l10n_in_journal_id = fields.Many2one('account.journal', string="Journal", \
        states=Purchase.READONLY_STATES, domain="[('type', '=', 'purchase')]",tracking=True)
    l10n_in_gst_treatment = fields.Selection([
            ('regular', 'Registered Business - Regular'),
            ('composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('consumer', 'Consumer'),
            ('overseas', 'Overseas'),
            ('special_economic_zone', 'Special Economic Zone'),
            ('deemed_export', 'Deemed Export')
        ], string="GST Treatment", states=Purchase.READONLY_STATES, compute="_compute_l10n_in_gst_treatment", store=True,tracking=True)
    l10n_in_company_country_code = fields.Char(related='company_id.account_fiscal_country_id.code', string="Country code",tracking=True)


    #sale_purchase


    sale_order_count = fields.Integer(
        "Number of Source Sale",
        compute='_compute_sale_order_count',
        groups='sales_team.group_sale_salesman',tracking=True)
    

    #purchase_mrp

    mrp_production_count = fields.Integer(
        "Count of MO Source",
        compute='_compute_mrp_production_count',
        groups='mrp.group_mrp_user',tracking=True)
    
    #purchase_stock    

    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', states={'done': [('readonly', True)]}, help="International Commercial Terms are a series of predefined commercial terms used in international transactions.",tracking=True)

    incoming_picking_count = fields.Integer("Incoming Shipment count", compute='_compute_incoming_picking_count',tracking=True)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking_ids', string='Receptions', copy=False, store=True,tracking=True)

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=Purchase.READONLY_STATES, required=True, default=_default_picking_type, domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
        help="This will determine operation type of incoming shipment",tracking=True)
    default_location_dest_id_usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage', string='Destination Location Type',
        help="Technical field used to display the Drop Ship Address", readonly=True,tracking=True)
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False,tracking=True)
    is_shipped = fields.Boolean(compute="_compute_is_shipped",tracking=True)
    effective_date = fields.Datetime("Effective Date", compute='_compute_effective_date', store=True, copy=False,
        help="Completion date of the first receipt order.",tracking=True)
    on_time_rate = fields.Float(related='partner_id.on_time_rate', compute_sudo=False,tracking=True)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"



    name = fields.Text(string='Description', required=True,tracking=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True,tracking=True)
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True,tracking=True)
    date_planned = fields.Datetime(string='Delivery Date', index=True,
        help="Delivery date expected from vendor. This date respectively defaults to vendor pricelist lead time then today's date.",tracking=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)],tracking=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]",tracking=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id',tracking=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True,tracking=True)
    product_type = fields.Selection(related='product_id.detailed_type', readonly=True,tracking=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price',tracking=True)

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True,tracking=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True,tracking=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True,tracking=True)

    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade',tracking=True)
    account_analytic_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account', compute='_compute_account_analytic_id', readonly=False,tracking=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags', compute='_compute_analytic_tag_ids', readonly=False,tracking=True)
    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Company', store=True, readonly=True,tracking=True)
    state = fields.Selection(related='order_id.state', store=True,tracking=True)

    


    # Replace by invoiced Qty
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", digits='Product Unit of Measure', store=True,tracking=True)

    qty_received_method = fields.Selection([('manual', 'Manual')], string="Received Qty Method", compute='_compute_qty_received_method', store=True,
        help="According to product configuration, the received quantity can be automatically computed by mechanism :\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n",tracking=True)
    qty_received = fields.Float("Received Qty", compute='_compute_qty_received', inverse='_inverse_qty_received', compute_sudo=True, store=True, digits='Product Unit of Measure',tracking=True)
    qty_received_manual = fields.Float("Manual Received Qty", digits='Product Unit of Measure', copy=False,tracking=True)
    qty_to_invoice = fields.Float(compute='_compute_qty_invoiced', string='To Invoice Quantity', store=True, readonly=True,
                                  digits='Product Unit of Measure',tracking=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True, store=True,tracking=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True,tracking=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True,tracking=True)
    product_packaging_id = fields.Many2one('product.packaging', string='Packaging', domain="[('purchase', '=', True), ('product_id', '=', product_id)]", check_company=True,tracking=True)
    product_packaging_qty = fields.Float('Packaging Quantity',tracking=True)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.",tracking=True)
    

    #sale_purchase

    sale_order_id = fields.Many2one(related='sale_line_id.order_id', string="Sale Order", store=True, readonly=True,tracking=True)
    sale_line_id = fields.Many2one('sale.order.line', string="Origin Sale Item", index=True, copy=False,tracking=True)

    #purchase_stock    

    qty_received_method = fields.Selection(selection_add=[('stock_moves', 'Stock Moves')],tracking=True)

    move_ids = fields.One2many('stock.move', 'purchase_line_id', string='Reservation', readonly=True, copy=False,tracking=True)
    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint', 'Orderpoint', copy=False, index=True,tracking=True)
    move_dest_ids = fields.One2many('stock.move', 'created_purchase_line_id', 'Downstream Moves',tracking=True)
    product_description_variants = fields.Char('Custom Description',tracking=True)
    propagate_cancel = fields.Boolean('Propagate cancellation', default=True,tracking=True)
    forecasted_issue = fields.Boolean(compute='_compute_forecasted_issue',tracking=True)