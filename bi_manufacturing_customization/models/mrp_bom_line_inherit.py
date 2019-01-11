# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    real_used_qty = fields.Float(
        'WQ', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)

    wested_qty = fields.Float(
        'RUQ', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)

    product_qty = fields.Float(compute='get_product_qty', string='Quantity', required=True, default=1.0)

    @api.depends('real_used_qty', 'wested_qty')
    def get_product_qty(self):
        for line in self:
            line.product_qty = line.real_used_qty + line.wested_qty

