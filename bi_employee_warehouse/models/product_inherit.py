# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    def _get_domain_locations(self):
        res = super(ProductProductInherit,self)._get_domain_locations()
        if self.env.context.get('with_user_warehouse') and self.env.user.warehouse_id and self.env.user.warehouse_id.lot_stock_id:
            res[0].append(('location_id','child_of',self.env.user.warehouse_id.lot_stock_id.id))
            return res
        return res