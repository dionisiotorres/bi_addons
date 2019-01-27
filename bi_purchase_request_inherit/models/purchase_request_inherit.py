# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.addons import decimal_precision as dp


class PurchaseRequestInherit(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def _default_operation_type(self):
        # to add the new implementation
        if self.env.user.operation_type_id:
            return self.env.user.operation_type_id.id
        else:
            return False

    def get_users_can_approved_purchase_request(self):
        all_users = self.env['res.users'].search([])
        users = [user.id for user in all_users if
                 user.has_group('bi_purchase_request_inherit.purchase_request_approve')]
        return [('id', 'in', users)]

    tag_ids = fields.Many2many(comodel_name='purchase.requests.tags', string='Tags')
    description_tree = fields.Text(string='Description', compute='description_tree_function')
    requested_by_employee_id = fields.Many2one('hr.employee', string='Requester Name')
    requested_for_employee_id = fields.Many2one('hr.employee', string='Requested For')
    department_id = fields.Many2one('hr.department', string='Department')
    hall_id = fields.Many2one('purchase.requests.hall', string='Hall')
    assigned_to = fields.Many2one('res.users', string='Approver', track_visibility='onchange',
                                  domain=lambda self: self.get_users_can_approved_purchase_request())
    picking_type_id = fields.Many2one('stock.picking.type',
                                      'Picking Type', default=_default_operation_type)
    request_date = fields.Date('Delivery Date', compute='_get_request_date', store=True)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state:
                raise ValidationError(_('You cannot delete purchase request.'))
        return super(PurchaseRequestInherit, self).unlink()

    @api.multi
    def write(self, values):
        user = self.env['res.users'].search([('id', '=', self._uid)])
        res = super(PurchaseRequestInherit, self).write(values)
        for order in self:
            if 'state' in values and values['state'] == 'approved':
                if 'line_ids' in values and not user.has_group('bi_purchase_request_inherit.purchase_request_validate'):
                    raise ValidationError(_("You are not allowed to validate purchase request to change lines."))
            elif 'state' not in values and order.state == 'approved':
                if 'line_ids' in values and not user.has_group('bi_purchase_request_inherit.purchase_request_validate'):
                    raise ValidationError(_("You are not allowed to validate purchase request to change lines."))
        return res

    @api.multi
    @api.depends('line_ids', 'line_ids.date_required')
    def _get_request_date(self):
        for rec in self:
            for line in rec.line_ids:
                rec.request_date = line.date_required
                break

    @api.multi
    def description_tree_function(self):
        for rec in self:
            n = rec.description or ''
            rec.description_tree = n[:30] + '...'

    @api.multi
    def button_validated(self):
        for rec in self:
            created_po = rec.make_purchase_order()
            mail_followers_object = self.env['mail.followers']
            if created_po:
                if 'domain' in created_po:
                    purchase_orders = self.env['purchase.order'].browse(created_po['domain'][0][-1])
                    for purchase_order in purchase_orders:
                        if purchase_order.origin and rec.name not in purchase_order.origin:
                            purchase_order.origin = purchase_order.origin + ' , ' + rec.name
                        else:
                            purchase_order.origin = rec.name

                        # add requested by to purchase request followers
                        if rec.requested_by.id != self._uid:
                            partner_follower_object = self.env['mail.followers'].sudo().search(
                                [('res_id', '=', purchase_order.id),
                                 ('partner_id', '=', rec.requested_by.partner_id.id)])
                            reg = {
                                'res_id': purchase_order.id,
                                'res_model': 'purchase.order',
                                'partner_id': rec.requested_by.partner_id.id,
                            }
                            if not partner_follower_object:
                                follower_id = mail_followers_object.sudo().create(reg)

        res = super(PurchaseRequestInherit, self).button_validated()
        return res

    @api.model
    def make_purchase_order(self):
        res = []
        purchase_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        pr_line_obj = self.env['purchase.request.line']
        created_pos = []
        for item in self.line_ids:
            if item.product_qty <= 0.0:
                raise exceptions.Warning(
                    _('Enter a positive quantity.'))
            location = item.request_id.picking_type_id.default_location_dest_id

            # get po with the same vendor
            purchase = False
            for created_po in created_pos:
                if item.vendor_id.id == created_po.partner_id.id:
                    purchase = created_po
                    break

            if not purchase:
                po_data = item._prepare_purchase_order(
                    item.request_id.picking_type_id, location,
                    item.company_id)
                purchase = purchase_obj.create(po_data)
                created_pos.append(purchase)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = item._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            new_pr_line = True
            if available_po_lines:
                new_pr_line = False
                po_line = available_po_lines[0]
                po_line.purchase_request_lines = [(4, item.id)]
            else:
                po_line_data = item._prepare_purchase_order_line(purchase,
                                                                 item)
                po_line = po_line_obj.create(po_line_data)

            # The onchange quantity is altering the scheduled date of the PO
            # lines. We do not want that:
            new_qty = pr_line_obj._calc_new_qty(
                item, po_line=po_line,
                new_pr_line=new_pr_line)
            po_line.product_qty = new_qty
            po_line._onchange_quantity()
            po_line.note = item.note

            po_line.date_planned = datetime.combine(item.date_required, datetime.min.time())
            res.append(purchase.id)

        return {
            'domain': [('id', 'in', res)],
            'name': _('RFQ'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }

    @api.model
    def create(self, vals):
        if not self.env.user.operation_type_id:
            raise ValidationError(_('Please configure operation type in current user related employee.'))
        vals.update({
            'requested_by': self.env.uid,
            'picking_type_id': self.env.user.operation_type_id.id,
        })
        res = super(PurchaseRequestInherit, self).create(vals)
        return res


class PurchaseRequestLineInherit(models.Model):
    _inherit = "purchase.request.line"

    date_required = fields.Date(string='Delivery Date', required=True,
                                track_visibility='onchange', default=False)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=1, domain=[('supplier', '=', True)])
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', related='product_id.uom_po_id', store=True)
    qty_onhand = fields.Float(string='Qty On Hand', digits=dp.get_precision('Product Unit of Measure'),
                              compute='_compute_qty_onhand', store=True)
    note = fields.Char(string='Note')

    @api.multi
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for rec in self:
            if rec.product_id:
                res = rec.product_id.with_context(with_user_warehouse=True,
                                                  company_owned=True)._compute_quantities_dict(False, False, False)
                rec.qty_onhand = res[rec.product_id.id]['qty_available']

    @api.onchange('product_id', 'product_qty')
    def _change_product(self):
        if self.product_id:
            if self.product_id.seller_ids:
                self.vendor_id = self.product_id.seller_ids[0].name
            else:
                self.vendor_id = False
                raise ValidationError(_('This product has no vendor'))

    @api.model
    def _prepare_purchase_order(self, picking_type, location, company):
        if not self.vendor_id:
            raise exceptions.Warning(
                _('Enter a supplier.'))
        supplier = self.vendor_id
        data = {
            'origin': '',
            'partner_id': supplier.id,
            'fiscal_position_id': supplier.property_account_position_id and
                                  supplier.property_account_position_id.id or False,
            'picking_type_id': picking_type.id,
            'company_id': company.id,
        }
        return data

    @api.model
    def _get_purchase_line_onchange_fields(self):
        return ['product_uom', 'price_unit', 'name',
                'taxes_id']

    @api.model
    def _execute_purchase_line_onchange(self, vals):
        cls = self.env['purchase.order.line']
        onchanges_dict = {
            'onchange_product_id': self._get_purchase_line_onchange_fields(),
        }
        for onchange_method, changed_fields in onchanges_dict.items():
            if any(f not in vals for f in changed_fields):
                obj = cls.new(vals)
                getattr(obj, onchange_method)()
                for field in changed_fields:
                    vals[field] = obj._fields[field].convert_to_write(
                        obj[field], obj)

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        product = item.product_id
        # Keep the standard product UOM for purchase order so we should
        # convert the product quantity to this UOM
        qty = item.product_uom_id._compute_quantity(
            item.product_qty, product.uom_po_id)
        # Suggest the supplier min qty as it's done in Odoo core
        min_qty = item._get_supplier_min_qty(product, po.partner_id)
        qty = max(qty, min_qty)
        vals = {
            'name': product.name,
            'order_id': po.id,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'price_unit': 0.0,
            'product_qty': qty,
            'account_analytic_id': item.analytic_account_id.id,
            'purchase_request_lines': [(4, item.id)],
            'date_planned': datetime.combine(item.date_required, datetime.min.time())
        }
        self._execute_purchase_line_onchange(vals)
        return vals

    @api.model
    def _get_purchase_line_name(self, order, line):
        product_lang = line.product_id.with_context({
            'lang': self.vendor_id.lang,
            'partner_id': self.vendor_id.id,
        })
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase
        return name

    @api.model
    def _get_order_line_search_domain(self, order, item):
        vals = item._prepare_purchase_order_line(order, item)
        name = item._get_purchase_line_name(order, item)
        order_line_data = [('order_id', '=', order.id),
                           ('name', '=', name),
                           ('product_id', '=', item.product_id.id or False),
                           ('date_planned', '=', item.date_required),
                           ('product_uom', '=', vals['product_uom']),
                           ('account_analytic_id', '=',
                            item.analytic_account_id.id or False),
                           ]
        if not item.product_id:
            order_line_data.append(('name', '=', item.name))
        return order_line_data

    @api.onchange('product_id')
    def onchange_product_id(self):
        # use purchase unit of measure
        res = super(PurchaseRequestLineInherit, self).onchange_product_id()
        if self.product_id:
            self.product_uom_id = self.product_id.uom_po_id.id
        return res
