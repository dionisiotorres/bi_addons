# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    real_used_qty = fields.Float(string="RUQ", default=1.0)
    wested_qty = fields.Float(string="WQ", default=1.0)
    product_qty = fields.Float(compute='get_product_qty', string='Quantity', required=True, default=1.0)

    @api.depends('real_used_qty', 'wested_qty')
    def get_product_qty(self):
        for line in self:
            line.product_qty = line.real_used_qty + line.wested_qty

