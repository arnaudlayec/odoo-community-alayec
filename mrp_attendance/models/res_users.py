# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResUsers(models.Model):
    _inherit = ["res.users"]

    manufacturing_worker = fields.Boolean(
        compute='_compute_manufacturing_worker',
        search='_search_manufacturing_worker',
    )
    mrp_time_ids = fields.One2many(
        string='Manufacturing Times',
        comodel_name='mrp.workcenter.productivity',
        inverse_name='user_id'
    )
    mrp_hours_today = fields.Float(compute='_compute_mrp_hours_today')

    #===== Compute =====#
    @api.depends('user_id', 'user_id.groups_id')
    def _compute_manufacturing_worker(self):
        mf_workers = self._get_mf_workers()
        for user in self:
            user.manufacturing_worker = user.id in mf_workers
    @api.model
    def _search_manufacturing_worker(self, operator, value):
        return [('id', 'in', self._get_mf_workers().ids)]
    def _get_mf_workers(self):
        return (
            self.env.ref('mrp_attendance.group_hr_attendance_mrp').users
            - self.env.ref('hr_attendance.group_hr_attendance_user').users
        )
    
    @api.depends('mrp_time_ids', 'mrp_time_ids.duration')
    def _compute_mrp_hours_today(self):
        rg_result = self.env['mrp.workcenter.productivity'].read_group(
            domain=[('user_id', 'in', self.ids), ('date', '=', fields.Date.today())],
            groupby=['user_id'],
            fields=['duration:sum']
        )
        mapped_duration = {x['user_id'][0]: x['duration'] for x in rg_result}

        for user in self:
            user.mrp_hours_today = mapped_duration.get(user.id, 0) / 60

    #===== Button 'Times of today' =====#
    def action_open_mrp_times_today(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Times of today'),
            'res_model': 'res.users',
            'res_id': self._context.get('mrp_attendance_user_id'),
            'views': [(self.env.ref('mrp_attendance.mrp_attendance_user_times_today').id, 'form')],
            'context': self._context | {
                'mrp_attendance': True,
                'workorder_display_name_simple': False, # full name on form
            },
            'target': 'new',
        }
