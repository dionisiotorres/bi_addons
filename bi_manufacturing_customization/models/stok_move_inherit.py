# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    real_used_qty = fields.Float(
        'WQ', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)

    wested_qty = fields.Float(
        'RUQ', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
