# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProjectProject(models.Model):
    _inherit = "project.project"

    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        domain=[('project_id', '=', False)],
        copy=False
    )

    _sql_constraints = [(
        "opportunity_id",
        "UNIQUE (opportunity_id)",
        "An opportunity may only be linked to one project."
    )]

    def write(self, vals):
        if 'opportunity_id' in vals or (self.opportunity_id.id and not vals.get('opportunity_id')):
            self._write_mirror_lead(vals.get('opportunity_id'))
        return super().write(vals)

    def _write_mirror_lead(self, opportunity_id):
        # Lead is unlinked from project's form
        if not opportunity_id:
            self.opportunity_id.project_id = False
        # New lead is linked
        else:
            self.env['crm.lead'].browse(opportunity_id).project_id = self
