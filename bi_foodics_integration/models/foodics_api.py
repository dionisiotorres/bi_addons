# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json
import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from odoo.exceptions import ValidationError

BASE_URL = 'https://dev-dash.foodics.com'
SECRET = 'NT4KBVXZ68U4K1A9U52I'

class FoodicsApi(models.Model):
    _name = 'foodics.api'

    name = fields.Char(string='Name', readonly=1)

    @api.model
    def get_token(self):
        request_url = BASE_URL + '/api/v2/token'
        data = {
            "secret": SECRET,
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.post(request_url, data=json.dumps(data), headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'token' in content:
                token = content['token']
            else:
                token = False
        except:
            token = False
        return token

    @api.model
    def get_business_hid(self, token):
        request_url = BASE_URL + '/api/v2/businesses'
        headers = {
            'Authorization': ('Bearer %s' % token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.get(request_url, headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'businesses' in content and len(content['businesses']) and 'hid' in content['businesses'][0]:
                business_hid = content['businesses'][0]['hid']
            else:
                business_hid = False
        except:
            business_hid = False
        return business_hid

    @api.model
    def get_headers(self):
        token = self.get_token()
        if token:
            business_hid = self.get_business_hid(token)
            if business_hid:
                headers = {
                    'Authorization': ('Bearer %s' % token),
                    'X-business': business_hid,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                return headers
            else:
                raise ValidationError(_('No Business HID found!'))
        else:
            raise ValidationError(_('Failed to get token!'))

    @api.model
    def get_branches(self, headers):
        request_url = BASE_URL + '/api/v2/branches'
        try:
            req = requests.get(request_url, headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'branches' in content:
                branches = content['branches']
            else:
                branches = False
        except:
            branches = False
        return branches

    @api.multi
    def get_data(self):
        headers = self.get_headers()
        branches = self.get_branches(headers)
        print('branches', branches)
