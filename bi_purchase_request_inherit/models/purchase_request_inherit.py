from odoo import fields, models, api


class PurchaseRequestInherit(models.Model):
    _inherit = 'purchase.request'

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

    @api.multi
    def description_tree_function(self):
        for rec in self:
            n = rec.description or ''
            rec.description_tree = n[:30] + '...'
