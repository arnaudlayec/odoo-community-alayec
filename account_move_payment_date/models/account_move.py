from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = ['account.move']

    byomelabs_payment_date = fields.Date(
        compute='_compute_byomelabs_payment_date', store=True,
        string="Date paiement Byomelabs", readonly=False,
        help="Par défaut, égal à la date de comptabilisation "
        "plus 1 mois, quinzaine suivante.")
