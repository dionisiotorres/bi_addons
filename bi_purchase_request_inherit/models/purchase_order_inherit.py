# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    note = fields.Char(string='Note')
    purchase_request_line_id = fields.Many2one('purchase.request', string='Purchase Request',
                                               compute='get_purchase_request')

    @api.multi
    def get_purchase_request(self):
        for purchase_order_line in self:
            if purchase_order_line.purchase_request_lines:
                purchase_order_line.purchase_request_line_id = purchase_order_line.purchase_request_lines[
                    0].request_id.id


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        request_line_id = self.env['purchase.request.line'].browse(self.env.context.get('active_ids', False))
        res.update({'note': request_line_id.note})
        return res

    @api.multi
    def make_purchase_order(self):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()
        request_line_id = self.env['purchase.request.line'].browse(self.env.context.get('active_ids', False))
        if 'domain' in res:
            purchase_order = self.env['purchase.order'].browse(res['domain'][0][-1])
            mail_followers_object = self.env['mail.followers']

            if request_line_id.requested_by.id != self._uid:
                reg = {
                    'res_id': purchase_order.id,
                    'res_model': 'purchase.order',
                    'partner_id': request_line_id.requested_by.partner_id.id,
                }
                follower_id = mail_followers_object.create(reg)

        return res
