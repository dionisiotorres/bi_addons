# -*- coding: utf-8 -*-

from odoo import api, fields, models, registry, _


class StockRuleInherit(models.Model):
    """ A rule describe what a procurement should do; produce, buy, move, ... """
    _inherit = 'stock.rule'

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        res = super(StockRuleInherit, self)._push_prepare_move_copy_values(move_to_copy, new_date)
        res.update({'push_rule': True, 'source_picking_id':move_to_copy.picking_id.id if move_to_copy.picking_id else False})
        return res
