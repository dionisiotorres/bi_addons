# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    employee_id = fields.Many2one('hr.employee', string="Received By")
    department_id = fields.Many2one('hr.department', string="Department")
    receive_date = fields.Date(string="Received Date")
    asset_history_ids = fields.One2many('asset.history', 'account_asset_id', string="Asset History")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountAssetAsset, self).create(vals_list)
        for vals in vals_list:
            if 'employee_id' in vals.keys():
                created_asset_history = self.env['asset.history'].create({
                    'employee_id': res.employee_id.id,
                    'department_id': vals['department_id'] if 'department_id' in vals.keys() else False,
                    'receive_date': vals['receive_date'] if 'receive_date' in vals.keys() else False,
                    'account_asset_id': res.id,
                })
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        if 'employee_id' in vals.keys():
            created_asset_history = self.env['asset.history'].create({
                'employee_id': vals['employee_id'],
                'department_id': self.department_id.id,
                'receive_date': self.receive_date,
                'account_asset_id': self.id,
            })
        return res
