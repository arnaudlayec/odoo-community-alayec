# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

class Partner(models.Model):
    _inherit = "res.partner"

    project_count = fields.Integer('Involved Projects', compute='_compute_project_count', compute_sudo=True)

    def _compute_project_count(self):
        """ Count related project, based on `project.contact_ids.partner_id`
            *and* `project.partner_id`. Don't simply use `search_count` because:
            - a same contact can be both client and stakeholder
            - a contact can be listed twice or more as stakeholder on a project
        """
        Project = self.sudo().env['project.project']
        rg_kwargs = {
            'domain': [('partner_id', 'in', self.ids)],
            'fields': ['project_ids:array_agg(id)'],
            'groupby': ['partner_id']
        }
        rg_client = Project.read_group(**rg_kwargs)
        rg_contact = Project.read_group(**rg_kwargs)
        mapped_client_ids = {x['partner_id'][0]: x['project_ids'] for x in rg_client}
        mapped_contact_ids = {x['partner_id'][0]: x['project_ids'] for x in rg_contact}
        for partner in self:
            partner.project_count = len(
                set(mapped_client_ids.get(partner.id, [])) | 
                set(mapped_contact_ids.get(partner.id, []))
            )

    def action_open_project_by_partner(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("project.open_view_project_all")
        domain = expression.AND([
            safe_eval(action.get('domain') or '[]'),
            ['|', ('partner_id', '=', self.id), ('contact_ids.partner_id', '=', self.id)]
        ])
        action.update({
            'name': _('Involved Projects'),
            'domain': action['domain']
        })
        return action
