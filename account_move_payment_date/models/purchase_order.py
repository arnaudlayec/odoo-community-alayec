# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Lead(models.Model):
    _inherit = 'crm.lead'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        copy=False
    )
    is_won = fields.Boolean(related='stage_id.is_won') # used in view

    _sql_constraints = [(
        "project_id",
        "UNIQUE (project_id)",
        "A project may only be linked to one opportunity."
    )]

    def action_create_project(self):
        """ Creates a project pre-filled from its opportunity and redirect to it """
        self.project_id = self.env['project.project'].sudo().create(
            self._get_copied_vals()
        )
        # redirect to the project
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
        }

    def _get_copied_vals(self):
        """ Can be overwritten """
        return {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'opportunity_id': self.id
        }
