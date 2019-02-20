# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    total_cost_price = fields.Monetary(string= 'Total Cost', compute= '_compue_total_cost')

    @api.multi
    @api.depends('standard_price','qty_available')
    def _compue_total_cost(self):
        for rec in self:
            rec.total_cost_price = rec.standard_price * rec.qty_available


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    def _get_domain_locations(self):
        if self.env.context.get('compute_report'):
            return super(ProductProductInherit, self.with_context(company_owned=False))._get_domain_locations()
        return super(ProductProductInherit, self)._get_domain_locations()
