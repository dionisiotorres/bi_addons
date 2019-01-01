# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'


    manual_mo = fields.Boolean(string='Manual MO')