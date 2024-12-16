# @author: Alexis de Lattre <alexis.delattre@akretion.com>

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # begin with context_ to allow user to change it by himself
    context_purchase_access_group_id = fields.Many2one(
        comodel_name='purchase.access.group',
        string="Default purchase group",
        ondelete='restrict'
    )
