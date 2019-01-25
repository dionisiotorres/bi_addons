# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_qty = fields.Float(string='Real Reserved Quantity', digits=dp.get_precision('Product Unit of Measure'), )
