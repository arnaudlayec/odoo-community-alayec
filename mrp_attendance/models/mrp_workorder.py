# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkorder(models.Model):
    _inherit = ["mrp.workorder"]
    _rec_names_search = ['name', 'production_id', 'product_id']

    #===== Fields methods =====#
    def name_get(self):
        if self._context.get('workorder_display_name_simple'):
            res = []
            for wo in self:
                index = wo.production_id.workorder_ids.ids.index(wo._origin.id) + 1
                res.append((wo.id, wo.display_name or wo.name or ''))
        else:
            res = super().name_get()
        return res

    # just add the tooltip
    name = fields.Char(help='Name displayed in Manufacturing Times view')
    duration_hours = fields.Float(
        string='Real Duration (h)',
        compute='_compute_duration_hours',
        digits=(16, 2),
    )
    duration_expected_hours = fields.Float(
        string='Expected Duration (h)',
        compute='_compute_duration_hours',
        inverse='_inverse_duration_hours',
        digits=(16, 2),
    )
    
    #===== Compute =====#
    @api.depends('duration', 'duration_expected')
    def _compute_duration_hours(self):
        for wo in self:
            wo.duration_hours = wo.duration / 60
            wo.duration_expected_hours = wo.duration_expected / 60
    def _inverse_duration_hours(self):
        for wo in self:
            wo.duration = wo.duration_hours * 60

    #===== Button (from MO kanban) =====#
    def action_open_productivity_attendance(self):
        """ Opens productivity form
            1. By default on the single workorder, if any
            2. (!) On the existing productivity of this day & workorder, if any
        """
        user_id = self._context.get('mrp_attendance_user_id')
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Manufacturing Times'),
            'res_model': 'mrp.workcenter.productivity',
            'view_mode': 'form',
            'context': self._context | {
                'mrp_attendance': True,
                'mrp_attendance_user_id': user_id,
                'default_production_id': self.production_id.id,
                'workorder_display_name_simple': False, # full name on form
            },
            'target': 'new',
        }

        suffix = ''
        if len(self) == 1:
            suffix = self.display_name
            action['context'] |= {'default_workorder_id': self.id}

            domain = [('user_id', '=', user_id), ('date', '=', fields.Date.today())]
            productivity = self.time_ids.filtered_domain(domain)
            if productivity:
                action['res_id'] = productivity.id
        else:
            suffix = self.production_id.display_name
        
        if suffix:
            action['name'] += ' / ' + suffix

        return action
