# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AssetHistory(models.Model):
    _name = 'asset.history'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Received By")
    department_id = fields.Many2one('hr.department', string="Department")
    receive_date = fields.Date(string="Received Date")
    delivered_date = fields.Date(string="Delivered Date")
    account_asset_id = fields.Many2one('account.asset.asset')
