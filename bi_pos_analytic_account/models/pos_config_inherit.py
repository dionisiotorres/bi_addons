# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import uuid4
import json
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')