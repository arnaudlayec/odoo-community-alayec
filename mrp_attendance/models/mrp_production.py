# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = ["mrp.production"]


    #===== Fields =====#
    user_logged_timed = fields.Boolean(
        compute='_compute_user_logged_timed',
        search='_search_user_logged_timed',
    )
    workcenter_ids = fields.Many2many(
        comodel_name='mrp.workcenter',
        compute='_compute_workcenter_ids',
        search='_search_workcenter_ids',
    )
    production_duration_hours_expected = fields.Float(
        string='Expected Duration (h)',
        compute='_compute_production_duration_expected'
    )
    production_real_duration_hours = fields.Float(
        string='Real Duration (h)',
        compute='_compute_production_real_duration'
    )


    #===== Native ORM methods overwritte =====#
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        vals_list = super().search_read(domain, fields, offset, limit, order, **read_kwargs)
        return self._search_read_filter_workorders(domain, vals_list)
    
    @api.model
    def _search_read_filter_workorders(self, domain, vals_list):
        """ Context: Kanban card of Manufacturing Orders lists their Work Orders.
             User may filter on Work Centers via SearchPanel on Work Center
            => this hack filters rendered `workorder_ids` field to in Kanban Card to
             the one belonging of Work Centers selected in SearchPanel
        """
        # Get native search panel domain & result
        mo_ids = [vals['id'] for vals in vals_list] # list of MO cards rendered in Kanban view
        wc_ids = self._get_domain_part(domain, 'workcenter_ids', 'in') # workcenters selected in searchpanel
        
        if mo_ids and wc_ids:
            domain = [('production_id', 'in', mo_ids), ('workcenter_id', 'in', wc_ids)]
            wo_ids_relevant = self.env['mrp.workorder'].sudo().search(domain).ids

            # filter render of field `workorder_ids`
            if wo_ids_relevant:
                for vals in vals_list:
                    wo_ids_orm = vals.get('workorder_ids', [])
                    vals['workorder_ids'] = [x for x in wo_ids_orm if x in wo_ids_relevant]

        return vals_list

    def _get_domain_part(self, domain, field, operator=None):
        """ Search a domain_part in a `domain according to tuples' 1st item (i.e. `field`)
            Return the value (3rd tuple item) of the 1st domain part found or False
        """
        domain_part = [
            part for part in domain
            if part[0] == field and (not(operator) or part[1] == operator)
        ]
        return bool(domain_part) and domain_part[0][2]
    
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
    
    @api.depends('workorder_ids', 'workorder_ids.workcenter_id')
    def _compute_workcenter_ids(self):
        for mo in self:
            mo.workcenter_ids = mo.workorder_ids.workcenter_id
    @api.model
    def _search_workcenter_ids(self, operator, value):
        domain = [('workcenter_id', operator, value)]
        mo_ids = self.env['mrp.workorder'].sudo().search(domain).production_id.ids
        return [('id', 'in', mo_ids)]

    # @api.depends is native
    def _compute_production_duration_expected(self):
        super()._compute_production_duration_expected()
        for mo in self:
            mo.production_duration_hours_expected = mo.production_duration_expected / 60
        
    def _compute_production_real_duration(self):
        super()._compute_production_real_duration()
        for mo in self:
            mo.production_real_duration_hours = mo.production_real_duration / 60

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
