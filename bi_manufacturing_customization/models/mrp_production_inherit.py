# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


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
    number_batches = fields.Integer(string="Number Of Batches", default=1)
    batch_quantity = fields.Float(string="Batch Quantity", digits=dp.get_precision('Product Unit of Measure'), compute='_compute_batch_quantity', store=True)
    # temp field for quantity to handle onchange with readonly issue
    product_qty_temp = fields.Float(
        'Temp Quantity To Produce', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
        states={'confirmed': [('readonly', False)]})

    def _generate_raw_move(self, bom_line, line_data):
        res = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        res.write({'real_used_qty': bom_line.real_used_qty * self.product_qty,
                   'wested_qty': bom_line.wested_qty * self.product_qty})
        return res

    @api.onchange('bom_id', 'number_batches')
    def _onchange_bom_id(self):
        self.product_qty = self.bom_id.product_qty * self.number_batches
        self.product_qty_temp = self.bom_id.product_qty * self.number_batches
        self.product_uom_id = self.bom_id.product_uom_id.id

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id)
            if bom.type == 'normal':
                self.bom_id = bom.id
                self.number_batches = 1
                self.product_qty = self.bom_id.product_qty * self.number_batches
                self.product_qty_temp = self.bom_id.product_qty * self.number_batches
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}


    @api.multi
    @api.depends('bom_id')
    def _compute_batch_quantity(self):
        for rec in self:
            rec.batch_quantity = rec.bom_id.product_qty

    @api.model
    def create(self, values):
        if values.get('product_qty_temp'):
            values['product_qty'] = values.get('product_qty_temp')
        return super(MrpProduction, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('product_qty_temp'):
            values['product_qty'] = values.get('product_qty_temp')
        return super(MrpProduction, self).write(values)
