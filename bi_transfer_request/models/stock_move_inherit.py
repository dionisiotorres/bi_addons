# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    # pass transfer request to picking
    def _get_new_picking_values(self):
        res = super(StockMoveInherit, self)._get_new_picking_values()
        if self.transfer_request_id:
            res.update({'transfer_request_id': self.transfer_request_id.id})
        return res