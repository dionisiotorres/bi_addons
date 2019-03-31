# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    start_at = fields.Datetime(string='Opening Date', readonly=False)
    expected_closing_at = fields.Datetime(string='Expected closing at')
    st_date = fields.Date(compute='_get_session_st_date', string='Start Date', store=True)

    @api.multi
    @api.depends('start_at')
    def _get_session_st_date(self):
        for rec in self:
            if rec.start_at:
                rec.st_date = rec.start_at.date()

    @api.multi
    def validate_pickings(self):
        self.ensure_one()
        # count = 1
        for order in self.order_ids.filtered(lambda l: l.picking_id.state not in ['done','cancel']):
            picking_id = order.picking_id
            # _logger.warning('POS Order: %s', count)
            picking_id.action_assign_foodics()
            picking_id.extra_force_assign()
            self.env['stock.immediate.transfer'].create(
                {'pick_ids': [(4, picking_id.id)]}).process()

            # wrong_lots = order.set_pack_operation_lot(picking_id)
            # if not wrong_lots:
            #     picking_id.action_done()
            # count += 1
        return True

    # prevent closing session if pickings are not done
    # @api.multi
    # def action_pos_session_closing_control(self):
    #     for rec in self:
    #         if rec.picking_count:
    #             raise ValidationError('Validate Pickings First.')
    #     return super(PosSessionInherit, self).action_pos_session_closing_control()
