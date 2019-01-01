# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    hid = fields.Char(string='HID', copy=False)
    size_hid = fields.Char(string='Size HID', copy=False)

    @api.constrains('hid', 'size_hid')
    def check_unique_hid(self):
        for rec in self:
            if rec.hid or rec.size_hid:
                if self.env['product.template'].search_count([('hid', '=', rec.hid), ('size_hid', '=', rec.size_hid)]) > 1:
                    raise ValidationError(_('This HID and size HID combination already exists.'))