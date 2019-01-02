from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import ValidationError
from datetime import datetime


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
        users = [user.id for user in all_users if user.has_group('bi_purchase_request_inherit.purchase_request_approve')]
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

    @api.multi
    def description_tree_function(self):
        for rec in self:
            n = rec.description or ''
            rec.description_tree = n[:30] + '...'

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.make_purchase_order()
        res = super(PurchaseRequestInherit, self).button_approved()
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

    vendor_id = fields.Many2one('res.partner', string='Vendor', required=1, domain=[('supplier', '=', True)])
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', related='product_id.uom_po_id', store=True)

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
            # 'product_qty': qty,
            'account_analytic_id': item.analytic_account_id.id,
            'purchase_request_lines': [(4, item.id)],
            'date_planned': datetime.combine(item.date_required, datetime.min.time())
        }
        # procurement dose not exist in odoo11
        # if item.line_id.procurement_id:
        #     vals['procurement_ids'] = [(4, item.line_id.procurement_id.id)]
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