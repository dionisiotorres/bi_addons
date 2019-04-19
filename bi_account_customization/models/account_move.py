# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    reference_order = fields.Char('Order Ref', compute='_get_reference_order', store=True)

    @api.multi
    @api.depends('invoice_id', 'move_id.stock_move_id', 'move_id.ref', 'move_id.stock_move_id.picking_id.origin')
    def _get_reference_order(self):
        for line in self:
            reference_order = False
            if line.invoice_id:
                reference_order = line.invoice_id.number

            elif line.move_id.stock_move_id.picking_id.origin:
                reference_order = line.move_id.stock_move_id.picking_id.origin

            else:
                reference_order = line.move_id.ref

            line.update({
                'reference_order': reference_order,
            })
