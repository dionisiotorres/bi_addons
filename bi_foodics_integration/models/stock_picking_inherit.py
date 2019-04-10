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
            ._action_confirm()
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        # self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed')\
        #     .mapped('move_lines')._action_assign()
        return True

    # server action method to validate pickings
    @api.multi
    def action_validate_picking_foodics(self):
        for picking_id in self:
            pos_order_id = self.env['pos.order'].search([('picking_id','=',picking_id.id)], limit=1)
            if pos_order_id:
                picking_id.action_assign_foodics()
                wrong_lots = pos_order_id.set_pack_operation_lot(picking_id)
                if not wrong_lots:
                    picking_id.action_done()
