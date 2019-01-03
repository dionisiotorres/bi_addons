# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    st_date = fields.Date(compute='_get_session_st_date', string='Start Date', store=True)

    @api.multi
    @api.depends('start_at')
    def _get_session_st_date(self):
        for rec in self:
            if rec.start_at:
                rec.st_date = rec.start_at.date()