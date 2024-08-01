from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            product_lines = {}
            for line in order.order_line:
                product = line.product_id
                if product not in product_lines:
                    product_lines[product] = self.env['sale.order.line']
                product_lines[product] |= line

            for product, lines in product_lines.items():
                picking_type_id = self.env['stock.picking.type'].search([("code", "=", 'outgoing')], limit=1)
                picking = self.env['stock.picking'].create({
                    'partner_id': order.partner_id.id,
                    'picking_type_id': picking_type_id.id,
                    'origin': order.name,
                    'location_id': order.warehouse_id.lot_stock_id.id,
                    'location_dest_id': order.partner_id.property_stock_customer.id,
                })
                for line in lines:
                    self.env['stock.move'].create({
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'picking_id': picking.id,
                        'location_id': order.warehouse_id.lot_stock_id.id,
                        'location_dest_id': order.partner_id.property_stock_customer.id,
                        'sale_line_id': line.id,
                    })
                picking.action_confirm()
                picking.action_assign()

        return res
