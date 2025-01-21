# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResUsers(models.Model):
    _inherit = ["res.users"]

    mrp_time_ids = fields.One2many(
        string='Manufacturing Times',
        comodel_name='mrp.workcenter.productivity',
        inverse_name='user_id'
    )
    mrp_time_ids_today = fields.One2many(
        string='Times of today',
        comodel_name='mrp.workcenter.productivity',
        compute='_compute_mrp_time_ids_today',
        inverse='_inverse_mrp_time_ids_today',
    )
    mrp_hours_today = fields.Float(compute='_compute_mrp_hours_today')

    #===== Compute =====#
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
    
    @api.depends('mrp_time_ids')
    def _compute_mrp_time_ids_today(self):
        today = fields.Date.today()
        for user in self:
            user.mrp_time_ids_today = user.mrp_time_ids.filtered(lambda x: x.date == today)
    def _inverse_mrp_time_ids_today(self):
        today = fields.Date.today()
        for user in self:
            # delete removed ones
            to_delete = user.mrp_time_ids.filtered(lambda x: x.date == today) - user.mrp_time_ids_today
            to_delete.unlink()
            
            # update vals of modified ones
            to_update = user.mrp_time_ids_today - to_delete
            for x in to_update:
                x._origin.write(x._prepare_vals())

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
