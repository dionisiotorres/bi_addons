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
        return super(StockQuantityHistoryInherit,self.with_context(location=location)).open_table()


    @api.onchange('compute_at_date')
    def onchange_compute_at_date(self):
        for rec in self:
            if not rec.compute_at_date:
                rec.location_id = False