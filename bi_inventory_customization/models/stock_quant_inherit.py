# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockQuantInherit(models.Model):
    _inherit = "stock.quant"

    total_cost_price = fields.Monetary(string= 'Total Cost', compute= '_compue_total_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id, readonly=True)

    @api.multi
    @api.depends('product_id','product_id.standard_price','quantity')
    def _compue_total_cost(self):
        for rec in self:
            rec.total_cost_price = rec.product_id.standard_price * rec.quantity