# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ApiImportException(models.Model):
    _name = 'api.import.exception'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    session_id = fields.Many2one('pos.session', string='Session')
    pos_id = fields.Many2one('pos.config', string='POS')