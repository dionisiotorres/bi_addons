# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    real_used_qty = fields.Float('RUQ')
    wested_qty = fields.Float('WQ')