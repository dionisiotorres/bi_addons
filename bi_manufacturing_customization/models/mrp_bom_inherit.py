# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    batch_quantity = fields.Float(string="Batch Quantity", digits=dp.get_precision('Product Unit of Measure'))