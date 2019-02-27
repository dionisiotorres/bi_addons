# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    total_cost_price = fields.Monetary(string= 'Total Cost', compute= '_compue_total_cost')

    @api.multi
    @api.depends('standard_price','qty_available')
    def _compue_total_cost(self):
        for rec in self:
            rec.total_cost_price = rec.standard_price * rec.qty_available


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    def _get_domain_locations(self):
        if self.env.context.get('compute_report'):
            return super(ProductProductInherit, self.with_context(company_owned=False))._get_domain_locations()
        return super(ProductProductInherit, self)._get_domain_locations()

    @api.multi
    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'stock_move_ids.remaining_value', 'product_tmpl_id.cost_method', 'product_tmpl_id.standard_price', 'product_tmpl_id.property_valuation', 'product_tmpl_id.categ_id.property_valuation')
    def _compute_stock_value(self):
        StockMove = self.env['stock.move']
        to_date = self.env.context.get('to_date')

        self.env['account.move.line'].check_access_rights('read')
        fifo_automated_values = {}
        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), sum(quantity), array_agg(aml.id)
                     FROM account_move_line AS aml
                     JOIN account_move am ON aml.move_id = am.id
                     JOIN stock_move sm ON am.stock_move_id = sm.id
                    WHERE aml.product_id IS NOT NULL AND aml.company_id=%%s %s %s %s
                 GROUP BY aml.product_id, aml.account_id"""
        params = (self.env.user.company_id.id,)
        additional_date_query = '%s'
        additional_location_query = '%s'
        additional_warehouse_query = '%s'

        if to_date:
            additional_date_query = additional_date_query % ('AND aml.date <= %s',)
            params = params + (to_date,)
        else:
            additional_date_query = additional_date_query % ('',)

        location = self.env.context.get('location')
        if location and self.env.context.get('compute_report'):
            additional_location_query = additional_location_query % ('AND (sm.location_dest_id = %s OR sm.location_id = %s)',)
            params = params + (location,location)
        else:
            additional_location_query = additional_location_query % ('',)

        warehouse = self.env.context.get('warehouse')
        if warehouse and self.env.context.get('compute_report'):
            additional_warehouse_query = additional_warehouse_query % ('AND sm.warehouse_id = %s',)
            params = params + (warehouse,)
        else:
            additional_warehouse_query = additional_warehouse_query % ('',)

        query = query %(additional_date_query,additional_location_query,additional_warehouse_query)
        self.env.cr.execute(query, params=params)

        res = self.env.cr.fetchall()
        for row in res:
            fifo_automated_values[(row[0], row[1])] = (row[2], row[3], list(row[4]))

        for product in self:
            if product.cost_method in ['standard', 'average']:
                qty_available = product.with_context(company_owned=True, owner_id=False).qty_available
                price_used = product.standard_price
                if to_date:
                    price_used = product.get_history_price(
                        self.env.user.company_id.id,
                        date=to_date,
                    )
                product.stock_value = price_used * qty_available
                product.qty_at_date = qty_available
            elif product.cost_method == 'fifo':
                if to_date:
                    if product.product_tmpl_id.valuation == 'manual_periodic':
                        domain = [('product_id', '=', product.id), ('date', '<=', to_date)] + StockMove._get_all_base_domain()
                        moves = StockMove.search(domain)
                        product.stock_value = sum(moves.mapped('value'))
                        product.qty_at_date = product.with_context(company_owned=True, owner_id=False).qty_available
                        product.stock_fifo_manual_move_ids = StockMove.browse(moves.ids)
                    elif product.product_tmpl_id.valuation == 'real_time':
                        valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
                        value, quantity, aml_ids = fifo_automated_values.get((product.id, valuation_account_id)) or (0, 0, [])
                        product.stock_value = value
                        product.qty_at_date = quantity
                        product.stock_fifo_real_time_aml_ids = self.env['account.move.line'].browse(aml_ids)
                else:
                    product.stock_value, moves = product._sum_remaining_values()
                    product.qty_at_date = product.with_context(company_owned=True, owner_id=False).qty_available
                    if product.product_tmpl_id.valuation == 'manual_periodic':
                        product.stock_fifo_manual_move_ids = moves
                    elif product.product_tmpl_id.valuation == 'real_time':
                        valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
                        value, quantity, aml_ids = fifo_automated_values.get((product.id, valuation_account_id)) or (0, 0, [])
                        product.stock_fifo_real_time_aml_ids = self.env['account.move.line'].browse(aml_ids)
