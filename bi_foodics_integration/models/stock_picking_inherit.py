# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        res = super(StockPickingInherit,self.sudo()).action_done()
        if self._context.get('keep_dates', False) and self._context.get('force_period_date', False):
            self.write({'date_done': self._context.get('force_period_date')})
        else:
            self.write({'date_done': fields.Datetime.now()})
        return res