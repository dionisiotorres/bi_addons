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


class PosOrderLineInherit(models.Model):
    _inherit = 'pos.order.line'

    hid = fields.Char(string='HID', copy=False)

    @api.constrains('hid')
    def check_unique_hid(self):
        for rec in self:
            if rec.hid:
                if self.env['pos.order.line'].search_count([('hid', '=', rec.hid)]) > 1:
                    raise ValidationError(_('This HID already exists.'))