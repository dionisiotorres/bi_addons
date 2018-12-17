# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    hid = fields.Char(string='HID', copy=False)

    # @api.constrains('hid')
    # def check_unique_hid(self):
    #     for rec in self:
    #         if rec.hid:
    #             if self.env['account.journal'].search_count([('hid', '=', rec.hid)]) > 1:
    #                 raise ValidationError(_('This HID already exists.'))