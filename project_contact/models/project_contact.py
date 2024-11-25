# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectContact(models.Model):
    _name = "project.contact"
    _description = "Project Contact"
    _order = 'project_id'

    category_id = fields.Many2one(
        'res.partner.category',
        string='Function',
        required=True,
        ondelete='cascade'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Stakeholder',
        required=True,
        ondelete='cascade'
    )

    _sql_constraints = [
        (
            "categ_uniq",
            "UNIQUE (category_id, project_id, partner_id)",
            "A contact may be assigned per role only once within a project.",
        ),
    ]

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ Pre-fill `category_id` with partner's 1st one """
        for contact in self.filtered(lambda x: not x.category_id.id):
            contact.category_id = fields.first(contact.partner_id.category_id)
