# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from odoo.osv import expression
from odoo.tools import date_utils

class HrEmployeeTimesheetCostHistory(models.Model):
    _inherit = ["hr.employee.timesheet.cost.history"]

    #===== Fields =====#
    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        comodel_name="account.analytic.account",
    )
    date_to = fields.Date(
        string='Date To',
        compute='_compute_date_to',
        store=True,
        readonly=True,
    )

    #===== Constrains =====#
    def _get_fields_related(self):
        """ :return: like ['employee_id', 'department_id', 'workcenter_id', 'analytic_account_id'] """
        return [
            name for name, attrs
            in self.fields_get().items()
            if attrs['type'] == 'many2one' and name not in ('create_uid', 'write_uid', 'currency_id')
        ]
    
    @api.constrains(lambda self: self._get_fields_related())
    def _constrain_only_one_m2o(self):
        for history in self:
            defined = [x for x in self._get_fields_related() if history[x].exists()]
            if len(defined) != 1:
                raise exceptions.ValidationError(_(
                    "One field (only) must be set amoung those: %s",
                    defined
                ))
    
    @api.ondelete(at_uninstall=False)
    def _unlink_if_related_not_set(self):
        """ Can only remove lines of `analytic_account_id` """
        if self._context.get('allow_unlink_cost_history'):
            return
        
        fields = [x for x in self._get_fields_related() if x != 'analytic_account_id']
        if any(self[field] for field in fields):
            raise exceptions.ValidationError(_(
                "Such line cannot be removed by a user."
            ))
    
    #===== Compute =====#
    @api.depends(lambda self:
        [x + '.timesheet_cost_history_ids.starting_date' for x in self._get_fields_related()]
    )
    def _compute_date_to(self):
        """ `date_to` is either:
            * `starting_date - 1 day` of next history in cost history, or
            * False if no next history
        """
        # if not starting_date, can't compute date_to (should never happen)
        no_starting_date = self.filtered(lambda x: not x.starting_date)
        no_starting_date.date_to = fields.Date.today()
        self = self - no_starting_date
        if not self.ids: # early quit for perf., if already finished
            self.date_to = False
            return
        
        # Get `starting_date`, per employee, department or workcenter
        fields_related = self._get_fields_related()
        domain = expression.OR([
            [(field, 'in', self[field].ids)] for field in fields_related
        ])
        rg_result = self.sudo().read_group(
            domain=domain,
            groupby=fields_related,
            fields=['starting_dates:array_agg(starting_date)'],
            lazy=False
        )
        mapped_data = {field: {} for field in fields_related}
        for x in rg_result:
            field = self._get_field(x)
            mapped_data[field][x[field][0]] = x['starting_dates']

        for history in self:
            field = history._get_field()
            if field:
                dates_from = mapped_data[field].get(history[field].id, []) # all `starting_date` of siblings history
                if dates_from:
                    next_starting_date = [date for date in dates_from if date and date > history.starting_date]
                    if next_starting_date:
                        history.date_to = date_utils.subtract(min(next_starting_date), days=1)
                        continue
            history.date_to = False
    
    def _get_field(self, vals=None):
        is_dict = bool(vals)
        if not is_dict:
            vals = self
        
        for field in self._get_fields_related():
            if vals[field] and (is_dict and vals[field][0] or vals[field].id):
                return field
        
        return None
    
    #===== Button =====#
    def button_open_details(self):
        """ On history costs tree view from Accounting app, to open Department or Employee form """

        field = self._get_field()
        model = self._get_fields_related().get(field)
        return {
            'type': 'ir.actions.act_window',
            'res_model': model,
            'res_id': self[field].id,
            'view_mode': 'form',
            'name': self[field].name,
            'context': {'display_analytic': True}
        }
