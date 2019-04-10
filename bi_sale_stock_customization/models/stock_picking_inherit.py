# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    date_done = fields.Datetime(string='Date of Transfer', copy=False, readonly=False, default=fields.Datetime.now,
                                help="Date at which the transfer has been processed or cancelled.")

    @api.multi
    @api.onchange('scheduled_date')
    def change_done_date(self):
        for record in self:
            record.date_done = record.scheduled_date

    @api.multi
    def action_done(self):
        if self.date_done:
            date_done = self.date_done
        else:
            date_done = fields.Datetime.now()
        super(StockPicking, self).action_done()
        self.write({'date_done': date_done})
        return True