# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = ["mrp.production"]

    user_logged_timed = fields.Boolean(
        compute='_compute_user_logged_timed',
        search='_search_user_logged_timed',
    )
    workcenter_ids = fields.Many2many(
        comodel_name='mrp.workcenter',
        compute='_compute_workcenter_ids',
        search='_search_workcenter_ids',
    )


    #===== Compute =====#
    @api.depends('workorder_ids.time_ids.user_id')
    def _compute_user_logged_timed(self):
        production_ids = self._get_mo_user_logged_time()
        for mo in self:
            mo.user_logged_timed = mo in production_ids
        
    @api.model
    def _search_user_logged_timed(self, operator, value):
        mo_ids = self._get_mo_user_logged_time().ids
        operator = 'in' if value else 'not in'
        return [('id', operator, mo_ids)]

    def _get_mo_user_logged_time(self):
        """ Returns MO on which user is working or haved worked """
        domain = [('user_id', '=', self._context.get('mrp_attendance_user_id'))]
        if self:
            domain += [('production_id', 'in', self.ids)]
        return self.env['mrp.workcenter.productivity'].search(domain).production_id

    
    @api.depends('workorder_ids.workcenter_id')
    def _compute_workcenter_ids(self):
        for mo in self:
            mo.workcenter_ids = mo.workorder_ids.workcenter_id
        
    @api.model
    def _search_workcenter_ids(self, operator, value):
        mo_ids = self.env['mrp.workorder'].sudo().search([('workcenter_id', operator, value)]).production_id.ids
        return [('id', 'in', mo_ids)]


    #===== Action =====#
    def _get_domain_mo_attendance(self):
        return [
            ('state', 'in', ['confirmed', 'progress', 'to_close']),
            ('workorder_ids', '!=', False)
        ]
    
    def action_open_productivity_attendance(self):
        """ Called on click of a Kanban card of a MO
            => Opens a productivity form
        """
        workorder_id = self._context.get('default_workorder_id')
        workorders = self.workorder_ids.browse(workorder_id) if workorder_id else self.workorder_ids
        return self.workorder_ids.action_open_productivity_attendance()
