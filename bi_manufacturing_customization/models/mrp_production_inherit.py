# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        res = super(ChangeProductionQty, self).change_prod_qty()
        self.change_move_lines_qty()
        return res

    @api.multi
    def change_move_lines_qty(self):
        for wizard in self:
            if wizard.mo_id.move_raw_ids:
                for move_line in wizard.mo_id.move_raw_ids:
                    for line in wizard.mo_id.bom_id.bom_line_ids:
                        if line.product_id == move_line.product_id:
                            move_line.real_used_qty = line.real_used_qty * wizard.product_qty
                            move_line.wested_qty = line.wested_qty * wizard.product_qty


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        oldname='product_uom', required=True, related='product_id.uom_id', store=True)

    def _generate_raw_move(self, bom_line, line_data):
        res = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        res.write({'real_used_qty': bom_line.real_used_qty * self.product_qty,
                   'wested_qty': bom_line.wested_qty * self.product_qty})
        return res