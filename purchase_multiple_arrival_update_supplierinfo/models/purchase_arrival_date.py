# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class PurchaseArrivalDate(models.Model):
    _inherit = ['purchase.arrival.date']

    verified = fields.Boolean(default=False)

    def action_verify_toggle(self):
        for arrival in self:
            arrival.verified = not arrival.verified
