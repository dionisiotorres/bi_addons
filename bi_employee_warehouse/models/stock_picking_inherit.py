# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        return super(StockPickingInherit,self.sudo()).button_validate()