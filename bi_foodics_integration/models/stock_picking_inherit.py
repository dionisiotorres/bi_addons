# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


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

    @api.multi
    def action_assign_foodics(self):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.filtered(lambda picking: picking.state == 'draft').action_confirm_foodics()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError(_('Nothing to check the availability for.'))
        # If a package level is done when confirmed its location can be different than where it will be reserved.
        # So we remove the move lines created when confirmed to set quantity done to the new reserved ones.
        package_level_done = self.mapped('package_level_ids').filtered(lambda pl: pl.is_done and pl.state == 'confirmed')
        package_level_done.write({'is_done': False})
        # moves._action_assign()
        # package_level_done.write({'is_done': True})
        return True


    @api.multi
    def action_confirm_foodics(self):
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        # call `_action_confirm` on every draft move
        self.mapped('move_lines')\
            .filtered(lambda move: move.state == 'draft')\
            ._action_confirm_foodics()
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        # self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
        #     .mapped('move_lines')._action_assign()
        return True

    # server action method to validate pickings
    @api.multi
    def action_validate_picking_foodics(self):
        for picking_id in self:
            picking_id.action_assign_foodics()
            picking_id.extra_force_assign()
            self.env['stock.immediate.transfer'].create(
                {'pick_ids': [(4, picking_id.id)]}).process()


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    def _action_confirm_foodics(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id, move.rule_id and move.rule_id.name or "/", origin,
                                              values)

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        self._push_apply()
        if merge:
            return self._merge_moves(merge_into=merge_into)
        return self