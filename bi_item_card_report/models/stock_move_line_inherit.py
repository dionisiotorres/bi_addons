# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from datetime import timedelta

InternalLocations = ['internal', 'production', 'transit']


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    opening_balance = fields.Float('Opening Balance', default=0.0, digits=dp.get_precision('Product Unit of Measure'),
                                   copy=False, compute='_compute_balance')
    qty_in = fields.Float('Quantity In', default=0.0, digits=dp.get_precision('Product Unit of Measure'), copy=False,
                          compute='_compute_quantities_and_cost')
    qty_out = fields.Float('Quantity Out', default=0.0, digits=dp.get_precision('Product Unit of Measure'), copy=False,
                           compute='_compute_quantities_and_cost')
    cost_price_in = fields.Float('In Cost', copy=False, compute='_compute_quantities_and_cost')
    cost_price_out = fields.Float('Out Cost', copy=False, compute='_compute_quantities_and_cost')
    balance = fields.Float('Balance', default=0.0, digits=dp.get_precision('Product Unit of Measure'), copy=False,
                           compute='_compute_balance')
    balance_cost = fields.Float('Balance Cost', default=0.0, digits=dp.get_precision('Product Unit of Measure'),
                                copy=False, compute='_compute_balance')

    def _check_move_locations(self, src_location_type, dest_location_type):
        if src_location_type in InternalLocations and dest_location_type in InternalLocations:
            return False
        if src_location_type == dest_location_type:
            return False
        return True

    @api.multi
    def _compute_balance(self):
        if self._context.get('date_from') and self._context.get('date_to'):
            domain = [('date', '>=', self._context.get('date_from')),
                      ('date', '<=', self._context.get('date_to')), ('state', '=', 'done')]
            if self._context.get('product_id', False):
                domain.append(('product_id', '=', self._context.get('product_id')))
            line_id = self.env['stock.move.line'].search(domain, limit=1, order='date')
        product_cost_value = {}
        for rec in self.env['stock.move.line'].search(domain, order='product_id,date,id'):
            if rec.product_id.id not in product_cost_value.keys():
                product_cost_value[rec.product_id.id] = [0.0,0.0]

            #calculate opening balance
            # opening_balance_date = + timedelta(days=1)
            if self._context.get('report_view', False) and self._context.get('product_id', False) and line_id and rec.id == line_id.id:
                product_id = self.env['product.product'].search([('id', '=', self._context.get('product_id'))])

                # qty at date
                product_cost_value[rec.product_id.id][0] = product_id.with_context(company_owned=True, owner_id=False,
                                                             to_date=self._context.get('date_from')).qty_available
                rec.opening_balance = product_id.with_context(company_owned=True, owner_id=False,
                                                              to_date=self._context.get('date_from')).qty_available
                # stock value at date
                price_used = product_id.get_history_price(
                    self.env.user.company_id.id,
                    date=self._context.get('date_from'),
                )
                product_cost_value[rec.product_id.id][1] = product_id.with_context(company_owned=True, owner_id=False,
                                                                  to_date=self._context.get(
                                                                      'date_from')).qty_available * price_used

            if self._context.get('report_view', False) and self._check_move_locations(rec.location_id.usage,
                                                                                      rec.location_dest_id.usage):
                if rec.qty_in:
                    rec.balance = product_cost_value[rec.product_id.id][0] + rec.qty_in
                    rec.balance_cost = product_cost_value[rec.product_id.id][1] + rec.move_id.value

                    product_cost_value[rec.product_id.id][0] = product_cost_value[rec.product_id.id][0] + rec.qty_in
                    product_cost_value[rec.product_id.id][1] = product_cost_value[rec.product_id.id][1] + rec.move_id.value
                elif rec.qty_out:
                    rec.balance = product_cost_value[rec.product_id.id][0] - rec.qty_out
                    rec.balance_cost = product_cost_value[rec.product_id.id][1] + rec.move_id.value

                    product_cost_value[rec.product_id.id][0] = product_cost_value[rec.product_id.id][0] - rec.qty_out
                    product_cost_value[rec.product_id.id][1] = product_cost_value[rec.product_id.id][1] + rec.move_id.value
            # if move for same location keep old values
            elif self._context.get('report_view', False) and not self._check_move_locations(rec.location_id.usage,
                                                                                            rec.location_dest_id.usage):
                rec.balance = product_cost_value[rec.product_id.id][0]
                rec.balance_cost = product_cost_value[rec.product_id.id][1]

    @api.multi
    def _compute_quantities_and_cost(self):
        for rec in self:
            if rec.location_dest_id and rec.location_dest_id.usage in InternalLocations:
                rec.qty_in = rec.qty_done
                rec.cost_price_in = rec.move_id.value if rec.move_id else 0.0
            else:
                rec.qty_out = rec.qty_done
                rec.cost_price_out = rec.move_id.value if rec.move_id else 0.0


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the non-stored fields that depend on the user context
        """
        res = super(StockMoveLineInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        stock_move_lines = self.env['stock.move.line']
        for line in res:
            if '__domain' in line:
                stock_move_lines = self.search(line['__domain'])
            if 'qty_in' in fields:
                line['qty_in'] = sum(stock_move_lines.mapped('qty_in'))
            if 'qty_out' in fields:
                line['qty_out'] = sum(stock_move_lines.mapped('qty_out'))
            if 'cost_price_in' in fields:
                line['cost_price_in'] = sum(stock_move_lines.mapped('cost_price_in'))
            if 'cost_price_out' in fields:
                line['cost_price_out'] = sum(stock_move_lines.mapped('cost_price_out'))
            if 'balance' in fields:
                line['balance'] = sum(stock_move_lines.mapped('qty_in')) - sum(stock_move_lines.mapped('qty_out'))
            if 'balance_cost' in fields:
                line['balance_cost'] = sum(stock_move_lines.mapped('cost_price_in')) + sum(stock_move_lines.mapped('cost_price_out'))
        return res
