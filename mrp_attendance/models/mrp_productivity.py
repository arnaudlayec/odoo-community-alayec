# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkcenterProductivity(models.Model):
    _inherit = ["mrp.workcenter.productivity"]

    #===== Fields methods =====#
    def _default_possible_workorder_ids(self):
        """ Within MO (if given) and not if already time set today on the workorder by this user """
        production = self.production_id or self.env['mrp.production'].browse(self._context.get('default_production_id'))
        if not production:
            production = production.search(production._get_domain_mo_attendance())
        
        user = self.user_id or self.env['res.users'].browse(self._context.get('mrp_attendance_user_id'))
        date = self.date or fields.Date.today()
        time_ids = user.mrp_time_ids.filtered(lambda x: x.date_start.date() == date)
        return production.workorder_ids - time_ids.workorder_id
    
    #===== Fields =====#
    mrp_attendance = fields.Boolean(
        store=False,
        default=lambda self: self._context.get('mrp_attendance')
    )
    # mrp
    production_id = fields.Many2one(store=True)
    workcenter_id = fields.Many2one(related='workorder_id.workcenter_id', store=True, readonly=False)
    workorder_id = fields.Many2one(domain="[('id', 'in', possible_workorder_ids)]")
    possible_workorder_ids = fields.One2many(
        string='Possible Workorders',
        comodel_name='mrp.workorder',
        default=_default_possible_workorder_ids,
        store=False
    )
    # user_id
    user_id = fields.Many2one(default=lambda self: self._context.get('mrp_attendance_user_id'))
    # date & time
    date_end = fields.Datetime(compute="_compute_date_end", store=True)
    duration_hours = fields.Float(
        string='Duration (h)',
        compute='_compute_duration_hours',
        store=True,
        readonly=False
    )
    date = fields.Date(compute='_compute_date', store=True)
    hours_today = fields.Float(required=True, compute='_compute_hours_today')

    #===== Compute =====#
    @api.depends('date_start')
    def _compute_date(self):
        for productivity in self:
            productivity.date = productivity.date_start and productivity.date_start.date()
    
    @api.depends('duration')
    def _compute_duration_hours(self):
        for productivity in self:
            productivity.duration_hours = productivity.duration / 60

    @api.depends('duration_hours')
    def _compute_duration(self):
        """ Neutralize compute : it becomes writable, and compute `date_end` instead
            Update when `duration_hours` is changed
        """
        for productivity in self:
            productivity.duration = productivity.duration_hours * 60
    
    @api.depends('duration', 'date_start')
    def _compute_date_end(self):
        for productivity in self:
            if productivity.date_start and productivity.duration:
                productivity.date_end = fields.Datetime.add(productivity.date_start, minutes=productivity.duration)

    @api.depends('duration_hours', 'user_id.mrp_time_ids', 'user_id.mrp_time_ids.duration')
    def _compute_hours_today(self):
        """ Real-time computing: other + this one """
        for productivity in self:
            productivity.hours_today = (
                self.user_id.mrp_hours_today
                - productivity._origin.duration_hours
                + productivity.duration_hours
            )
    
    def _prepare_vals(self):
        self.ensure_one()
        return {
            'company_id': self.company_id.id,
            'production_id': self.production_id.id,
            'workcenter_id': self.workcenter_id.id,
            'workorder_id': self.workorder_id.id,
            'user_id': self.user_id.id,
            'duration': self.duration,
            'loss_id': self.loss_id.id,
            'description': self.description,
        }

    #===== Button 'Times of today' =====#
    def action_open_mrp_times_today(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Times of today'),
            'res_model': 'mrp.workcenter.productivity',
            'views': [(self.env.ref('mrp_attendance.oee_tree_view_attendance').id, 'tree')],
            'domain': [
                ('user_id', '=', self._context.get('mrp_attendance_user_id')),
                ('date', '=', fields.Date.today())
            ],
            'context': self._context | {
                'mrp_attendance': True,
                'workorder_display_name_simple': False, # full name on form
            },
            'target': 'new',
        }
    
    def unlink_and_reopen(self):
        self.unlink()
        return self.action_open_mrp_times_today()
    
    #===== Synch with attendance =====#
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)._synch_with_attendance()
    
    def write(self, vals):
        res = super().write(vals)
        self._synch_with_attendance()
        return res

    def unlink(self):
        dates = self.mapped('date')
        res = super().unlink()
        self._synch_with_attendance(dates)
        return res

    def _synch_with_attendance(self, dates=[]):
        return self
