# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockQuantityHistoryInherit(models.TransientModel):
    _inherit = 'stock.quantity.history'

    location_id = fields.Many2one('stock.location', 'Location', domain="[('usage', 'in', ['internal','transit'])]")

    def open_table(self):
        self.ensure_one()
        location = False
        if self.compute_at_date and self.location_id:
            location = self.location_id.id

        if not self.env.context.get('valuation'):
            return super(StockQuantityHistoryInherit, self.with_context(location=location)).open_table()

        self.env['stock.move']._run_fifo_vacuum()

        if self.compute_at_date:
            tree_view_id = self.env.ref('stock_account.view_stock_product_tree2').id
            form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
            search_view_id = self.env.ref('stock_account.view_inventory_valuation_search').id
            # We pass `to_date` in the context so that `qty_available` will be computed across
            # moves until date.
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Inventory Valuation'),
                'res_model': 'product.product',
                'domain': "[('type', '=', 'product'), ('qty_available', '!=', 0)]",
                'context': dict(self.env.context, to_date=self.date, company_owned=False, create=False, edit=False,
                                location=location),
                'search_view_id': search_view_id
            }
            return action
        else:
            return self.env.ref('stock_account.product_valuation_action').read()[0]

    @api.onchange('compute_at_date')
    def onchange_compute_at_date(self):
        for rec in self:
            if not rec.compute_at_date:
                rec.location_id = False
