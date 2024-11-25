# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Users(models.Model):
    _inherit = ["res.users"]

    favorite_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Favorite project',
        compute='_computed_favorite_project_id',
        store=True
    )
    favorite_project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='favorite_user_ids',
        string='Favorite projects',
        readonly=True
    )
    
    @api.depends('favorite_project_ids')
    def _computed_favorite_project_id(self):
        for user in self:
            user.favorite_project_id = user.favorite_project_ids.ids[0] if len(user.favorite_project_ids) == 1 else False
