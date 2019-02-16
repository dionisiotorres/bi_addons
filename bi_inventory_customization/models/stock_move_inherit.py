# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    push_rule = fields.Boolean(string='Push Rule?')

    # preventing move merge with old pickings
    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        for move in self:
            recompute = False
            if move.push_rule:
                picking = False
            else:
                picking = move._search_picking_for_assignation()
            if picking:
                if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            move._assign_picking_post_process(new=recompute)
            # If this method is called in batch by a write on a one2many and
            # at some point had to create a picking, some next iterations could
            # try to find back the created picking. As we look for it by searching
            # on some computed fields, we have to force a recompute, else the
            # record won't be found.
            if recompute:
                move.recompute()
        return True

    #pass analytic account to picking entry
    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id):
        res = super(StockMoveInherit, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id)
        if res.get('debit_line_vals', False) and self.picking_id and self.picking_id.sale_id and self.picking_id.sale_id.analytic_account_id:
            res['debit_line_vals'].update({
                'analytic_account_id': self.picking_id.sale_id.analytic_account_id.id,
            })
        return res