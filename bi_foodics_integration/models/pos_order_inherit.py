# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    hid = fields.Char(string='HID', copy=False)

    @api.constrains('hid')
    def check_unique_hid(self):
        for rec in self:
            if rec.hid:
                if self.env['pos.order'].search_count([('hid', '=', rec.hid)]) > 1:
                    raise ValidationError(_('This HID already exists.'))


    # inherit to set entry date to session start date
    def _prepare_bank_statement_line_payment_values(self, data):
        args = super(PosOrderInherit, self)._prepare_bank_statement_line_payment_values(data)
        args.update({
            'date': self.session_id.start_at.date()
        })
        return args


class PosOrderLineInherit(models.Model):
    _inherit = 'pos.order.line'

    hid = fields.Char(string='HID', copy=False)

    @api.constrains('hid')
    def check_unique_hid(self):
        for rec in self:
            if rec.hid:
                if self.env['pos.order.line'].search_count([('hid', '=', rec.hid)]) > 1:
                    raise ValidationError(_('This HID already exists.'))