from odoo import fields, models, api


class PurchaseRequestsTags(models.Model):
    _name = 'purchase.requests.tags'

    name = fields.Char(string='Tag Name', required=True)


class PurchaseRequestHall(models.Model):
    _name = 'purchase.requests.hall'

    name = fields.Char(string='Hall', required=True)
