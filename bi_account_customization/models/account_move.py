# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ref_order = fields.Char('Order Ref', compute='_get_ref_order', store=True)

    @api.multi
    @api.depends('invoice_id', 'invoice_id.origin', 'move_id', 'move_id.stock_move_id',
                 'move_id.stock_move_id.picking_id.group_id')
    def _get_ref_order(self):
        for line in self:
            ref_order = False
            if line.invoice_id.origin:
                ref_order = line.invoice_id.origin

            elif line.move_id.stock_move_id.picking_id.group_id:
                ref_order = line.move_id.stock_move_id.picking_id.group_id

            line.update({
                'ref_order': ref_order,
            })
