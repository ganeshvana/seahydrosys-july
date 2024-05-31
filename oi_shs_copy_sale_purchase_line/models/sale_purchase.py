from odoo import api, fields, models, _

        

# class SaleOrder(models.Model):
#     _inherit = 'sale.order.line'

#     def copy_sale_order_line(self):
#         new_line = self.copy(default={'order_id': self.order_id.id})

#         sorted_lines = self.order_id.order_line.sorted(key=lambda x: x.sequence)

#         new_line.write({'sequence': sorted_lines[-1].sequence + 1})

#         return True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def copy_purchase_order_line(self):
        new_line = self.copy(default={'order_id': self.order_id.id})

      
        sorted_lines = self.order_id.order_line.sorted(key=lambda x: x.sequence)

        new_line.write({'sequence': sorted_lines[-1].sequence + 1})

        return True



