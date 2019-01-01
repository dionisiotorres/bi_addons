# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    prod_type = fields.Selection([
        ('semi', 'Semi Finished'),
        ('raw', 'Raw Material'),
    ], string='Product Type', related='categ_id.prod_type')


class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    prod_type = fields.Selection([
        ('semi', 'Semi Finished'),
        ('raw', 'Raw Material'),
    ], string='Product Type')