# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockRuleInherit(models.Model):
    _inherit = 'stock.rule'

    # pass transfer request to the newly created move
    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        res = super(StockRuleInherit, self)._push_prepare_move_copy_values(move_to_copy, new_date)
        if move_to_copy.transfer_request_id:
            origin = res.get('origin') + ',' + move_to_copy.transfer_request_id.name
            res.update({'transfer_request_id': move_to_copy.transfer_request_id.id, 'origin': origin})
        return res